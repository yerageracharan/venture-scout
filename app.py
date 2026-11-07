from __future__ import annotations
import json
import os
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from venture_scout.models import Company, Source, DimensionEvidence, DIMENSIONS
from venture_scout.store import Store
from venture_scout.scoring import score_company, diligence_gaps
from venture_scout.memo import build_memo
from venture_scout.llm import draft_ai_diligence
from venture_scout.cohort import analyse_cohort, analyse_outcomes
from venture_scout.sources.google_news import search_google_news
from venture_scout.sources.sec_edgar import discover_form_d

load_dotenv()
st.set_page_config(page_title="Venture Scout", page_icon="🔎", layout="wide")
st.title("Venture Scout")
st.caption("Evidence-first seed-stage venture intelligence · San Francisco · independent research")
st.warning("Independent research tool; not affiliated with a16z or any VC firm. Screening scores are prioritisation aids, not investment recommendations.")
DB_PATH = os.getenv("VENTURE_SCOUT_DB", "data/venture_scout.db")
store = Store(DB_PATH)


def seed_database() -> None:
    seed_path = Path("data/research_seeds.json")
    if store.get_all() or not seed_path.exists():
        return
    for record in json.loads(seed_path.read_text(encoding="utf-8")):
        store.upsert(Company.from_dict(record))


seed_database()
companies = store.get_all()
tabs = st.tabs(["Company universe", "Discover", "Diligence", "Cohort patterns", "Methodology"])

with tabs[0]:
    st.subheader("Startup universe")
    q = st.text_input("Search company, sector, investor or description")
    sectors = sorted({c.sector for c in companies if c.sector})
    sector = st.selectbox("Sector", ["All"] + sectors)
    filtered = [c for c in companies if (not q or q.lower() in " ".join([c.name,c.sector,c.description," ".join(c.investors)]).lower()) and (sector == "All" or c.sector == sector)]
    verified = [c for c in filtered if c.funding_evidence_status == "announced_verified" and c.round_amount_usd]
    unverified = [c for c in filtered if c.round_amount_usd and c.funding_evidence_status != "announced_verified"]
    m1,m2,m3 = st.columns(3)
    m1.metric("Companies", len(filtered))
    m2.metric("Verified announced capital", f"${sum(c.round_amount_usd or 0 for c in verified)/1e6:,.1f}M")
    m3.metric("Unverified funding leads", len(unverified))
    rows=[]
    for c in filtered:
        s=score_company(c)
        rows.append({"Company":c.name,"Sector":c.sector,"Stage":c.stage,"Round":f"${c.round_amount_usd/1e6:.1f}M" if c.round_amount_usd else "Unknown","Evidence":c.funding_evidence_status,"Score":s["score"],"Coverage":f'{s["coverage"]:.0f}%',"Screen":s["verdict"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("Only company/investor announcement-backed records marked announced_verified contribute to verified funding totals.")
    st.download_button("Export company universe (JSON)", json.dumps([c.to_dict() for c in filtered],indent=2), "venture-scout-universe.json", "application/json")
    if filtered:
        csv = pd.DataFrame(rows).to_csv(index=False)
        st.download_button("Export summary (CSV)", csv, "venture-scout-universe.csv", "text/csv")

with tabs[1]:
    st.subheader("Discover funding announcements")
    st.write("News search is a lead generator, not a complete or verified private-market database.")
    query = st.text_input("Search terms", value="San Francisco startup seed funding")
    days = st.slider("Lookback window (days)", 30, 730, 365, 30)
    limit = st.slider("Maximum results", 10, 100, 50, 10)
    if st.button("Search Google News RSS", type="primary"):
        try:
            st.session_state["news_leads"] = search_google_news(query, days=days, limit=limit)
        except Exception as exc:
            st.error(f"News search failed: {exc}")
    leads = st.session_state.get("news_leads", [])
    if leads:
        st.metric("Candidate articles", len(leads))
        st.dataframe(pd.DataFrame(leads), use_container_width=True, hide_index=True)
        candidate_names = [f'{i+1}. {r["company_candidate"] or r["title"][:70]}' for i,r in enumerate(leads)]
        selected = st.selectbox("Save candidate as a research lead", range(len(leads)), format_func=lambda i: candidate_names[i])
        if st.button("Save selected lead to company universe"):
            lead=leads[selected]
            name=lead["company_candidate"] or lead["title"][:100]
            record=Company(name=name, description=lead["excerpt"], round_amount_usd=lead["amount_usd_candidate"], round_date=lead["published_at"], funding_evidence_status="announced_unverified", sources=[Source(title=lead["title"],url=lead["url"],publisher="Google News RSS",published_at=lead["published_at"],excerpt=lead["excerpt"],source_type="secondary")],notes="Auto-discovered news lead. Verify company identity, San Francisco location, stage, round amount and original announcement.")
            store.upsert(record)
            st.success(f"Saved {name} as an unverified lead.")
    st.divider()
    st.subheader("SEC Form D discovery (optional)")
    st.caption("A Form D is an exempt-offering notice, not proof of a priced seed round. Review issuer entity type, geography, offering amount and amount sold separately.")
    sec_email = st.text_input("SEC User-Agent contact (required by SEC fair-access guidance)", value=os.getenv("SEC_USER_AGENT",""))
    sec_days = st.slider("SEC filing lookback (days)", 30, 365, 120, 30, key="sec_days")
    if st.button("Search SEC Form D filings"):
        if "@" not in sec_email:
            st.error("Enter a descriptive User-Agent including a contact email.")
        else:
            try:
                st.session_state["sec_filings"]=discover_form_d(date.today()-timedelta(days=sec_days),date.today(),sec_email)
            except Exception as exc:
                st.error(f"SEC search failed: {exc}")
    filings=st.session_state.get("sec_filings",[])
    if filings:
        st.dataframe(pd.DataFrame(filings),use_container_width=True,hide_index=True)

with tabs[2]:
    st.subheader("Diligence workspace")
    names = {f"{c.name} · {c.company_id}": c for c in companies}
    if not names:
        st.info("No companies yet. Import or create a record in the Discover tab.")
    else:
        chosen = st.selectbox("Select company", list(names))
        company = names[chosen]
        score = score_company(company)
        a,b,c=st.columns(3)
        a.metric("Evidence-weighted score", score["score"] if score["score"] is not None else "—")
        b.metric("Evidence coverage", f'{score["coverage"]:.0f}%')
        c.metric("Screening disposition", score["verdict"])
        st.write(score["recommended_action"])
        st.markdown("#### Company snapshot")
        st.write(company.description or "No description recorded.")
        st.write("**Investors:** " + (", ".join(company.investors) or "Not verified"))
        st.write("**Funding evidence:** " + company.funding_evidence_status)
        with st.form("diligence_form"):
            st.markdown("#### Evidence-backed dimension ratings")
            st.caption("Rate only when you can write an evidence note. Add source URLs where possible. Blank is unknown, not zero.")
            updated={}
            for key,spec in DIMENSIONS.items():
                old=company.dimensions.get(key,DimensionEvidence())
                st.markdown(f"**{spec['label']} — {spec['weight']}%**")
                rating=st.selectbox(f"Rating · {spec['label']}",[0,1,2,3,4,5],index=(old.rating or 0),format_func=lambda x:"Not assessed" if x==0 else f"{x}/5",key=f"{company.company_id}_{key}_rating")
                evidence=st.text_area(f"Evidence · {spec['label']}",value=old.evidence,key=f"{company.company_id}_{key}_evidence",height=70)
                urls=st.text_input(f"Source URLs (comma-separated) · {spec['label']}",value=", ".join(old.source_urls),key=f"{company.company_id}_{key}_urls")
                updated[key]=DimensionEvidence(rating=rating or None,evidence=evidence,source_urls=[u.strip() for u in urls.split(",") if u.strip()])
            founder=st.text_area("Founder-market fit notes",value=company.founder_notes)
            customer=st.text_area("Customer / usage evidence",value=company.customer_evidence)
            gtm=st.text_area("Go-to-market motion",value=company.go_to_market)
            economics=st.text_area("Unit economics / capital intensity",value=company.economics)
            risks=st.text_area("Risks and disconfirming evidence",value=company.risks)
            outcome=st.selectbox("Observed outcome",["Unknown","Active","Follow-on round","Acquired","Shut down","Other"],index=["Unknown","Active","Follow-on round","Acquired","Shut down","Other"].index(company.outcome_status))
            outcome_date=st.text_input("Outcome date (YYYY-MM-DD)",value=company.outcome_date)
            outcome_url=st.text_input("Outcome evidence URL",value=company.outcome_evidence_url)
            save=st.form_submit_button("Save diligence record",type="primary")
            if save:
                company.dimensions=updated
                company.founder_notes=founder
                company.customer_evidence=customer
                company.go_to_market=gtm
                company.economics=economics
                company.risks=risks
                company.outcome_status=outcome
                company.outcome_date=outcome_date
                company.outcome_evidence_url=outcome_url
                store.upsert(company)
                st.success("Saved.")
                st.rerun()
        st.markdown("#### Diligence gaps")
        for gap in diligence_gaps(company):
            st.write(f"- {gap}")
        st.markdown("#### Investment memo")
        st.download_button("Download deterministic memo",build_memo(company),f"{company.name.lower().replace(' ','-')}-memo.md","text/markdown")
        if st.button("Generate optional AI-assisted memo"):
            try:
                st.session_state["ai_memo"]=draft_ai_diligence(company)
            except Exception as exc:
                st.error(f"AI memo unavailable: {exc}")
        if st.session_state.get("ai_memo"):
            st.markdown(st.session_state["ai_memo"])
            st.download_button("Download AI memo",st.session_state["ai_memo"],f"{company.name.lower().replace(' ','-')}-ai-memo.md","text/markdown")

with tabs[3]:
    st.subheader("Cohort patterns")
    stats=analyse_cohort(companies)
    a,b,c,d=st.columns(4)
    a.metric("Companies",stats["company_count"])
    b.metric("Verified funding announcements",stats["funded_records"])
    c.metric("Unverified leads",stats["unverified_funding_leads"])
    d.metric("Median announced round",f'${stats["median_round_usd"]/1e6:.1f}M' if stats["median_round_usd"] else "—")
    st.metric("Verified announced capital",f'${stats["total_announced_usd"]/1e6:,.1f}M')
    st.write("**Sector counts**")
    st.dataframe(pd.DataFrame(stats["sector_counts"],columns=["Sector","Companies"]),use_container_width=True,hide_index=True)
    st.write("**Investor frequency (verified announcement sample only)**")
    st.dataframe(pd.DataFrame(stats["investor_counts"],columns=["Investor","Mentions"]),use_container_width=True,hide_index=True)
    st.info(stats["caveat"])
    outcome=analyse_outcomes(companies)
    st.write("**Observed company outcomes**")
    st.write(f'{outcome["labelled_companies"]} companies have an outcome label.')
    if outcome["outcome_counts"]:
        st.dataframe(pd.DataFrame(outcome["outcome_counts"],columns=["Outcome","Count"]),hide_index=True)
    st.caption(outcome["warning"])

with tabs[4]:
    st.subheader("Methodology & guardrails")
    st.markdown("### Nine-dimension scoring rubric")
    st.dataframe(pd.DataFrame([{"Dimension":v["label"],"Weight":v["weight"],"Question":v["question"]} for v in DIMENSIONS.values()]),use_container_width=True,hide_index=True)
    st.markdown("""
    - Scores require a 1–5 rating and a written evidence note.
    - Unassessed dimensions remain unknown; they are not converted to zero.
    - Weighted evidence coverage below 60%, or fewer than five assessed dimensions, produces INSUFFICIENT EVIDENCE.
    - News aggregation discovers leads; original company/investor announcements verify funding claims.
    - SEC Form D is an exempt-offering notice. It does not establish a seed label or prove money was fully raised.
    - Cohort comparisons are descriptive and vulnerable to selection bias and survivorship bias.
    - No score is a probability of success, fair value, or investment recommendation.
    """)
    st.markdown("### Data source notes")
    st.write("Starter cohort sources are recorded in data/research_seeds.json. Check each source and preserve the distinction between company-announced funding, secondary reporting, and regulatory filings.")
