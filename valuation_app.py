import streamlit as st
import streamlit.components.v1 as components 
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# --- INJECTION DU CODE ADSENSE GLOBAL & BALISES DE VÉRIFICATION ---
# Ce code est injecté en haut de page (simule le <head>) pour la vérification du site par Google et la plateforme partenaire.
def inject_adsense_head():
    adsense_verification_script = """
    <!-- Code Global AdSense (Validation Google) -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5805757737293445"
         crossorigin="anonymous"></script>
    
    <!-- Balise de Vérification IMPACT SITE (Affiliation/Partenariat) -->
    <meta name='impact-site-verification' value='50d9a746-1376-4819-9331-960b659a868b'>
    
    <div style="display:none;">Verification Tags Holder</div>
    """
    components.html(adsense_verification_script, height=0, width=0)

# Configuration de la page avec le nouveau nom de marque
st.set_page_config(page_title="True Stock Price", layout="wide", page_icon="💰")
inject_adsense_head()

# --- GESTION DES LANGUES (INTERNATIONALISATION) ---
lang_option = st.sidebar.selectbox(
    "🌍 Language / Langue",
    ["English 🇺🇸", "Français 🇫🇷"],
    index=0
)

# Dictionnaire de textes (Marque mise à jour sans .com)
TRANS = {
    "Français 🇫🇷": {
        "disclaimer_title": "⚠️ AVERTISSEMENT IMPORTANT",
        "disclaimer_text": """
<strong>CECI N'EST PAS UN CONSEIL EN INVESTISSEMENT.</strong><br><br>
Les résultats fournis par <strong>True Stock Price</strong> sont générés à titre <strong>éducatif</strong>. Investir comporte des risques.
Faites vos propres recherches. L'éditeur décline toute responsabilité.""",
        "main_title": "💰 True Stock Price",
        "subtitle": "La vérité sur le prix des actions. Analysez, Valorisez, Investissez.",
        "sb_search": "1. Recherche",
        "sb_search_help": "Tapez le nom d'une entreprise (ex: L'Oréal) ci-dessous pour trouver son symbole.",
        "sb_ticker": "Symbole Sélectionné",
        "sb_btn": "🔍 Lancer l'Analyse",
        "sb_graph": "2. Affichage Graphique",
        "sb_period": "Historique :",
        "sb_settings": "3. Pilotage Hypothèses",
        "sb_override": "Activer le Mode Manuel",
        "ad_broker_title": "Courtier Recommandé",
        "ad_broker_desc": "Arrêtez de payer des frais inutiles.",
        "ad_broker_btn": "Voir l'offre Spéciale →",
        "res_market_price": "Prix Marché",
        "res_fair_value": "Vraie Valeur (TruePrice)",
        "res_undervalued": "SOUS-ÉVALUÉ (Opportunité)",
        "res_overvalued": "SUR-ÉVALUÉ (Trop cher)",
        "res_fair": "JUSTE PRIX (Correct)",
        "res_safety": "Prix cible sûr :",
        "tab_synth": "📊 Synthèse Stratégique",
        "tab_fin": "🧮 Détails Financiers",
        "tab_tech": "📈 Technique & Historique",
        "sig_tech": "Signal Technique :",
        "sig_buy": "FEU VERT",
        "sig_sell": "FEU ROUGE",
        "sig_neutral": "NEUTRE",
        "desc_company": "📝 Description de l'entreprise",
        "analysis_complete": "Analyse terminée pour",
        "err_data": "Données insuffisantes ou flux négatifs.",
        "loading": "True Stock Price analyse les données...",
        "search_placeholder": "Rechercher une entreprise (ex: Nvidia)...",
        "search_label": "🔍 Trouver un symbole",
        "found_msg": "Résultats trouvés :"
    },
    "English 🇺🇸": {
        "disclaimer_title": "⚠️ IMPORTANT DISCLAIMER",
        "disclaimer_text": """
<strong>THIS IS NOT INVESTMENT ADVICE.</strong><br><br>
Results provided by <strong>True Stock Price</strong> are for <strong>educational purposes only</strong>. Investing involves risk.
Do your own due diligence. The publisher assumes no responsibility.""",
        "main_title": "💰 True Stock Price",
        "subtitle": "The truth about stock prices. Analyze, Valuate, Invest.",
        "sb_search": "1. Research",
        "sb_search_help": "Type a company name below to find its ticker symbol.",
        "sb_ticker": "Selected Ticker",
        "sb_btn": "🔍 Analyze",
        "sb_graph": "2. Chart Settings",
        "sb_period": "History Period:",
        "sb_settings": "3. Assumptions Control",
        "sb_override": "Enable Manual Override",
        "ad_broker_title": "Recommended Broker",
        "ad_broker_desc": "Stop paying unnecessary fees.",
        "ad_broker_btn": "See Special Offer →",
        "res_market_price": "Market Price",
        "res_fair_value": "True Value",
        "res_undervalued": "UNDERVALUED (Opportunity)",
        "res_overvalued": "OVERVALUED (Expensive)",
        "res_fair": "FAIR PRICE (Correct)",
        "res_safety": "Safe buy price:",
        "tab_synth": "📊 Strategy Summary",
        "tab_fin": "🧮 Financial Details",
        "tab_tech": "📈 Technicals & Chart",
        "sig_tech": "Technical Signal:",
        "sig_buy": "GREEN LIGHT",
        "sig_sell": "RED LIGHT",
        "sig_neutral": "NEUTRE",
        "desc_company": "📝 Company Description",
        "analysis_complete": "Analysis complete for",
        "err_data": "Insufficient data or negative cash flows.",
        "loading": "True Stock Price is analyzing...",
        "search_placeholder": "Search company (e.g. Nvidia)...",
        "search_label": "🔍 Trouver un symbole",
        "found_msg": "Found results:"
    }
}

# Sélection de la langue active
T = TRANS[lang_option]

# --- DISCLAIMER LÉGAL (PROTECTION) ---
def show_legal_disclaimer():
    st.warning(T['disclaimer_title'])
    st.markdown(f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; color: #856404; font-size: 0.9em;'>{T['disclaimer_text']}</div>", unsafe_allow_html=True)

show_legal_disclaimer()

st.title(T['main_title'])
st.markdown(T['subtitle'])

# --- FONCTION DE RECHERCHE UNIVERSELLE (YAHOO API) ---
def search_symbol(query):
    """Cherche un ticker via l'API Yahoo Finance"""
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            return data['quotes']
    except:
        return []
    return []

# --- BARRE LATÉRALE (PARAMÈTRES) ---
st.sidebar.header(T['sb_search'])

# --- MOTEUR DE RECHERCHE DANS LA SIDEBAR ---
with st.sidebar.expander(T['search_label'], expanded=True):
    search_query = st.text_input(T['search_placeholder'], key="search_box")
    if search_query:
        results = search_symbol(search_query)
        if results:
            st.caption(T['found_msg'])
            options = {f"{r['symbol']} - {r.get('shortname', r.get('longname', 'N/A'))} ({r.get('exchange', 'N/A')})": r['symbol'] for r in results}
            selected_option = st.radio("Sélectionner :", list(options.keys()), label_visibility="collapsed")
            
            if selected_option:
                st.session_state['ticker_input'] = options[selected_option]
        else:
            st.caption("Aucun résultat trouvé.")

# Input principal
if 'ticker_input' not in st.session_state:
    st.session_state['ticker_input'] = "TSLA"

ticker_input = st.sidebar.text_input(T['sb_ticker'], key='ticker_input')
launch_btn = st.sidebar.button(T['sb_btn'], type="primary")

st.sidebar.header(T['sb_graph'])
period_label = st.sidebar.selectbox(
    T['sb_period'],
    ["1Y", "5Y", "10Y", "Max"],
    index=1
)
period_map = {"1Y": "1y", "5Y": "5y", "10Y": "10y", "Max": "max"}
selected_period = period_map[period_label]

st.sidebar.markdown("---")
st.sidebar.header(T['sb_settings'])
enable_override = st.sidebar.checkbox(T['sb_override'])

# --- SYSTÈME DE PUBLICITÉ (ADSENSE) ---
def show_adsense_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.caption("Ad / Publicité")
    # Slot ID par défaut, sera mis à jour après la validation AdSense
    adsense_code = """
    <div style="text-align: center; width: 100%;">
        <!-- Bloc Sidebar (Carré) -->
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-5805757737293445" 
             data-ad-slot="1234567890" 
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
        <div style="background: #f1f5f9; border: 2px dashed #cbd5e1; color: #64748b; padding: 20px 10px; border-radius: 8px; font-size: 11px;">
            Espace Pub Google<br>(Visible sur True Stock Price)
        </div>
    </div>
    """
    components.html(adsense_code, height=250)

def show_adsense_banner():
    st.markdown("---")
    st.caption("Ad / Publicité")
    # Slot ID par défaut, sera mis à jour après la validation AdSense
    adsense_code = """
    <div style="text-align: center; width: 100%;">
        <!-- Bloc Bannière (Bas) -->
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-5805757737293445"
             data-ad-slot="0987654321"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
        <div style="background: #f8fafc; border: 2px dashed #94a3b8; color: #475569; padding: 20px; border-radius: 8px;">
            Bannière Google AdSense<br><span style="font-size: 12px;">(Visible sur True Stock Price)</span>
        </div>
    </div>
    """
    components.html(adsense_code, height=150)

# --- SYSTÈME D'AFFILIATION (MONÉTISATION) ---
def show_affiliate_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🏆 {T['ad_broker_title']}")
    
    # [LIEN 1 : TRADE REPUBLIC] MODIFIEZ CE LIEN PAR VOTRE LIEN PARTENAIRE TRADE REPUBLIC
    affiliate_link = "https://traderepublic.com/?ref=TR_BEST_OFFER" 
    
    html_card = f"""
    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="font-size: 28px; margin-bottom: 8px;">📈</div>
        <h4 style="margin: 0; color: #0f172a; font-size: 16px; font-weight: 700;'>Trade Republic</h4>
        <p style="font-size: 12px; color: #64748b; margin: 8px 0 16px 0;">{T['ad_broker_desc']}</p>
        
        <div style="background-color: #dcfce7; border: 1px solid #86efac; border-radius: 6px; padding: 6px; margin-bottom: 12px;">
            <span style="font-size: 11px; font-weight: 700; color: #166534;">🎁 BONUS: 1 Action / Stock*</span>
        </div>
        
        <a href="{affiliate_link}" target="_blank" style="display: block; width: 100%; background-color: #111827; color: white; text-align: center; padding: 10px 0; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; transition: background 0.3s;">
            {T['ad_broker_btn']}
        </a>
    </div>
    """
    st.sidebar.markdown(html_card, unsafe_allow_html=True)

def show_contextual_buttons(ticker):
    st.markdown("### 🛒 Action / Trade")
    c1, c2, c3 = st.columns(3)
    
    # [LIEN 2 : ETORO] A REMPLACER PAR VOTRE CODE D'AFFILIATION
    # Utilise le ticker dynamique
    link_etoro = f"https://www.etoro.com/markets/{ticker.replace('.PA', '')}?ref=VOTRE_CODE_ETORO" 
    
    # [LIEN 3 : INTERACTIVE BROKERS (IBKR)] CODE INTEGRE AVEC VOTRE ID edison546
    # Le lien complet est utilisé pour s'assurer que le parrainage est crédité.
    link_ibkr = "https://ibkr.com/referral/edison546" 
    
    # [LIEN 4 : TRADINGVIEW] A REMPLACER PAR VOTRE CODE D'AFFILIATION
    link_tradingview = "https://fr.tradingview.com/?aff=VOTRE_CODE_TV" 
    
    c1.markdown(f"""
    <a href="{link_etoro}" target="_blank" style="text-decoration: none;">
        <div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 15px; text-align: center; background: white; hover: bg-gray-50;">
            <span style="font-weight: bold; color: #16a34a;">eToro</span><br>
            <span style="font-size: 12px; color: #4b5563;">Buy {ticker} (0% Comm)</span>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    c2.markdown(f"""
    <a href="{link_ibkr}" target="_blank" style="text-decoration: none;">
        <div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 15px; text-align: center; background: white;">
            <span style="font-weight: bold; color: #ea580c;">Interactive Brokers (IBKR)</span><br>
            <span style="font-size: 12px; color: #4b5563;">Trader {ticker} (Pro)</span>
        </div>
    </a>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <a href="{link_tradingview}" target="_blank" style="text-decoration: none;">
        <div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 15px; text-align: center; background: white;">
            <span style="font-weight: bold; color: #2563eb;">TradingView</span><br>
            <span style="font-size: 12px; color: #4b5563;">Analyse Graphique</span>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Affichage des pubs sidebar
show_affiliate_sidebar()
show_adsense_sidebar()

# --- MOTEUR INTELLIGENT (Fondamental) ---

def determine_assumptions(info):
    assumptions = {}
    sector = info.get('sector', 'Unknown')
    beta = info.get('beta', 1.0)
    current_pe = info.get('trailingPE', None)
    forward_pe = info.get('forwardPE', None)
    if beta is None: beta = 1.0
    
    pe_reference = forward_pe if forward_pe and forward_pe > 0 else current_pe
    
    is_tech = 'Technology' in sector or 'Consumer Cyclical' in sector or 'Communication' in sector
    is_momentum = (pe_reference and pe_reference > 35) or info.get('revenueGrowth', 0) > 0.15
    assumptions['is_growth'] = is_tech or is_momentum
    assumptions['sector'] = sector

    rev_growth = info.get('revenueGrowth', 0.05)
    earn_growth = info.get('earningsGrowth', 0.05)
    raw_growth = max(rev_growth if rev_growth else 0, earn_growth if earn_growth else 0)
    
    if assumptions['is_growth']:
        assumptions['growth_rate'] = min(max(raw_growth * 0.9 * 100, 5.0), 40.0) / 100
    else:
        assumptions['growth_rate'] = min(max(raw_growth * 0.8 * 100, 2.0), 10.0) / 100

    market_cap = info.get('marketCap', 0)
    wacc_base = 3.5 + (beta * 4.0)
    if market_cap > 100_000_000_000: wacc_base -= 1.0
    assumptions['discount_rate'] = min(max(wacc_base, 6.0), 11.0) / 100

    if assumptions['is_growth']:
        assumptions['terminal_method'] = "multiple"
        if pe_reference and pe_reference > 0:
            target_multiple = pe_reference * 0.9
            target_multiple = min(max(target_multiple, 15.0), 60.0)
        else:
            target_multiple = 30.0
        assumptions['exit_multiple'] = target_multiple
        assumptions['perpetual_rate'] = 0.0
    else:
        assumptions['terminal_method'] = "perpetual"
        assumptions['exit_multiple'] = 0
        assumptions['perpetual_rate'] = 0.02

    industry = info.get('industry', 'Unknown')
    if 'Technology' in sector:
        if 'Semiconductors' in industry: peers = "NVDA, AMD, INTC, TSM"
        else: peers = "AAPL, MSFT, GOOGL, META"
    elif 'Consumer Cyclical' in sector: 
        if 'Auto' in industry: peers = "TM, F, GM, BYDDF"
        else: peers = "AMZN, WMT, TGT"
    elif 'Financial' in sector: peers = "JPM, BAC, V"
    else: peers = "SPY"
    assumptions['peers'] = peers
    return assumptions

def calculate_technical_indicators(history):
    if history.empty: return None, None, None
    history['SMA_50'] = history['Close'].rolling(window=50).mean()
    history['SMA_200'] = history['Close'].rolling(window=200).mean()
    delta = history['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    history['RSI'] = 100 - (100 / (1 + rs))
    latest = history.iloc[-1]
    return latest['RSI'], latest['SMA_50'], latest['SMA_200']

def get_financial_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        hist_period = "2y" if period == "1y" else period 
        history = stock.history(period=hist_period)
        rsi, sma50, sma200 = calculate_technical_indicators(history)
        
        # Filtre history pour l'affichage
        if period == "1y": history = history.tail(252)
        elif period == "5y": history = history.tail(252*5)
        
        cashflow = stock.cashflow
        financials = stock.financials 
        if cashflow.empty and financials.empty: return None
        
        def get_fcf_from_col(col_data):
            try:
                ocf = col_data.get('Total Cash From Operating Activities', col_data.get('Operating Cash Flow'))
                capex = col_data.get('Capital Expenditures', col_data.get('Capital Expenditure'))
                if ocf is not None and capex is not None: return ocf + capex
                return None
            except: return None

        fcf_last = get_fcf_from_col(cashflow.iloc[:, 0]) if not cashflow.empty else None
        
        fcf_avg = fcf_last
        if not cashflow.empty and cashflow.shape[1] >= 3:
            f1, f2, f3 = [get_fcf_from_col(cashflow.iloc[:, i]) for i in range(3)]
            if None not in [f1, f2, f3]: fcf_avg = (f1 + f2 + f3) / 3

        net_income = None
        if not financials.empty:
            net_income = financials.iloc[:, 0].get('Net Income')
            if net_income is None: net_income = financials.iloc[:, 0].get('Net Income Common Stockholders')
        if net_income is None: net_income = info.get('netIncomeToCommon', 0)

        bs = stock.balance_sheet
        total_debt = bs.iloc[:, 0].get('Total Debt', info.get('totalDebt', 0)) if not bs.empty else info.get('totalDebt', 0)
        cash = bs.iloc[:, 0].get('Cash And Cash Equivalents', info.get('totalCash', 0)) if not bs.empty else info.get('totalCash', 0)
        
        if total_debt is None: total_debt = 0
        if cash is None: cash = 0

        health_metrics = {
            "debt_to_equity": info.get('debtToEquity', None),
            "current_ratio": info.get('currentRatio', None),
            "return_on_equity": info.get('returnOnEquity', None),
            "profit_margins": info.get('profitMargins', None),
            "dividend_yield": info.get('dividendYield', None)
        }
        
        tech_metrics = {
            "rsi": rsi,
            "sma_50": sma50,
            "sma_200": sma200
        }

        return {
            "price": info.get('currentPrice', 0),
            "currency": info.get('currency', 'USD'),
            "shares": info.get('sharesOutstanding', 0),
            "fcf_last": fcf_last,
            "fcf_avg": fcf_avg,
            "net_income": net_income,
            "target_price": info.get('targetMeanPrice', None),
            "net_debt": total_debt - cash,
            "total_cash": cash,
            "total_debt": total_debt,
            "health": health_metrics,
            "tech": tech_metrics,
            "name": info.get('shortName', ticker),
            "summary": info.get('longBusinessSummary', 'No description.'),
            "pe_ratio": info.get('trailingPE', None),
            "market_cap": info.get('marketCap', 0),
            "beta": info.get('beta', 1.0),
            "info_obj": info, 
            "history": history
        }
    except Exception as e:
        return None

def calculate_enterprise_value(flow, assumptions):
    growth = assumptions['growth_rate']
    discount = assumptions['discount_rate']
    
    future_flows = []
    for i in range(1, 6):
        val = flow * ((1 + growth) ** i)
        future_flows.append(val / ((1 + discount) ** i))
        
    flow_year_5 = flow * ((1 + growth) ** 5)
    
    if assumptions['terminal_method'] == "multiple":
        terminal_val = flow_year_5 * assumptions['exit_multiple']
    else:
        perp = assumptions['perpetual_rate']
        terminal_val = (flow_year_5 * (1 + perp)) / (discount - perp)
        
    discounted_terminal = terminal_val / ((1 + discount) ** 5)
    return sum(future_flows) + discounted_terminal

def calculate_sensitivity_matrix(base_flow, assumptions, net_debt, shares):
    base_growth = assumptions['growth_rate']
    base_wacc = assumptions['discount_rate']
    growth_range = [base_growth - 0.01, base_growth, base_growth + 0.01]
    wacc_range = [base_wacc - 0.01, base_wacc, base_wacc + 0.01]
    results = []
    for w in wacc_range:
        row = []
        for g in growth_range:
            temp_assumptions = assumptions.copy()
            temp_assumptions['growth_rate'] = g
            temp_assumptions['discount_rate'] = w
            ev = calculate_enterprise_value(base_flow, temp_assumptions)
            equity_val = ev - net_debt
            val_per_share = equity_val / shares
            row.append(val_per_share)
        results.append(row)
    cols = [f"Growth {g:.1%}" for g in growth_range]
    idx = [f"WACC {w:.1%}" for w in wacc_range]
    df = pd.DataFrame(results, columns=cols, index=idx)
    return df

# --- AFFICHAGE ET EXÉCUTION ---

if 'override_growth' not in st.session_state: st.session_state['override_growth'] = 0.0
if 'override_wacc' not in st.session_state: st.session_state['override_wacc'] = 0.0
if 'override_multiple' not in st.session_state: st.session_state['override_multiple'] = 0.0

if launch_btn or st.session_state.get('data_loaded', False):
    if launch_btn:
        with st.spinner(T['loading']):
            data = get_financial_data(ticker_input, period=selected_period)
            if data:
                st.session_state['data'] = data
                st.session_state['data_loaded'] = True
                init_assumptions = determine_assumptions(data['info_obj'])
                st.session_state['override_growth'] = init_assumptions['growth_rate'] * 100
                st.session_state['override_wacc'] = init_assumptions['discount_rate'] * 100
                st.session_state['override_multiple'] = init_assumptions['exit_multiple']
            else:
                st.error(T['err_data'])

    if st.session_state.get('data_loaded', False):
        data = st.session_state['data']
        assumptions = determine_assumptions(data['info_obj'])
        
        if enable_override:
            st.sidebar.markdown(f"### 🛠️ {T['sb_settings']}")
            assumptions['growth_rate'] = st.sidebar.slider("Growth / Croissance (%)", 0.0, 50.0, st.session_state['override_growth'], 0.5) / 100
            assumptions['discount_rate'] = st.sidebar.slider("WACC / Risque (%)", 4.0, 15.0, st.session_state['override_wacc'], 0.1) / 100
            if assumptions['terminal_method'] == 'multiple':
                assumptions['exit_multiple'] = st.sidebar.slider("Exit Multiple (x)", 5.0, 100.0, st.session_state['override_multiple'], 1.0)

        earnings_val = data['net_income'] if data['net_income'] is not None else 0
        fcf_val = data['fcf_last'] if data['fcf_last'] is not None else 0
        
        if assumptions['is_growth']:
            base_flow = max(fcf_val, earnings_val)
        else:
            base_flow = fcf_val

        if base_flow > 0:
            ev = calculate_enterprise_value(base_flow, assumptions)
            equity_val = ev - data['net_debt']
            model_fair_value = equity_val / data['shares']
            
            analyst_target = data['target_price']
            if analyst_target and analyst_target > 0 and not enable_override:
                final_fair_value = (model_fair_value * 0.7) + (analyst_target * 0.3)
            else:
                final_fair_value = model_fair_value

            margin = 0.10 if assumptions['is_growth'] else 0.20
            safe_buy_price = final_fair_value * (1 - margin)
            diff = ((final_fair_value - data['price']) / data['price']) * 100

            # ONGLETS D'AFFICHAGE
            tab1, tab2, tab3 = st.tabs([T['tab_synth'], T['tab_fin'], T['tab_tech']])

            with tab1:
                st.subheader(f"{T['analysis_complete']} {data['name']}")
                
                c_r1, c_r2, c_r3 = st.columns(3)
                with c_r1:
                    st.metric(T['res_market_price'], f"{data['price']:.2f} {data['currency']}")
                with c_r2:
                    color = "normal"
                    if diff > 15: color = "normal" 
                    elif diff < -15: color = "inverse"
                    st.metric(T['res_fair_value'], f"{final_fair_value:.2f} {data['currency']}", delta=f"{diff:.1f}%", delta_color=color)
                with c_r3:
                    verdict_fund = "Neutre"
                    if diff > 15: verdict_fund = T['res_undervalued']
                    elif diff < -15: verdict_fund = T['res_overvalued']
                    else: verdict_fund = T['res_fair']
                    st.metric("Verdict", verdict_fund)

                st.progress(min(max((final_fair_value - 0) / (max(final_fair_value, data['price']) * 1.2), 0.0), 1.0))
                
                st.markdown("---")
                tech = data['tech']
                rsi = tech['rsi'] if tech['rsi'] else 50
                sma50 = tech['sma_50']
                
                c_t1, c_t2 = st.columns(2)
                with c_t1:
                    st.write(f"**{T['sig_tech']}**")
                    score_tech = 0
                    if rsi < 40: score_tech += 1
                    if sma50 and data['price'] > sma50: score_tech += 1
                    
                    if score_tech == 2: st.success(f"🟢 {T['sig_buy']}")
                    elif score_tech == 0: st.error(f"🔴 {T['sig_sell']}")
                    else: st.warning(f"🟠 {T['sig_neutral']}")
                
                with c_t2:
                    st.write(f"**RSI (14) :** {rsi:.0f}")
                    st.caption(" < 30 : Buy Zone | > 70 : Danger Zone")

                with st.expander(T['desc_company']):
                    st.write(data['summary'])
                
                st.markdown("---")
                show_contextual_buttons(ticker_input)

            with tab2:
                st.subheader("Deep Dive / Détails")
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Growth**\n\n{assumptions['growth_rate']:.1%}")
                c2.info(f"**WACC**\n\n{assumptions['discount_rate']:.1%}")
                c3.info(f"**Exit x**\n\n{assumptions['exit_multiple']:.1f}x")
                
                st.markdown("### Health / Santé")
                h = data['health']
                c_h1, c_h2, c_h3, c_h4 = st.columns(4)
                
                de = h.get('debt_to_equity')
                val_de = de if de and de < 10 else (de/100 if de else 0)
                c_h1.metric("Debt/Equity", f"{val_de:.2f}", delta="High" if val_de > 2 else "Ok", delta_color="inverse")
                
                roe = h.get('return_on_equity')
                c_h3.metric("ROE", f"{roe*100:.1f}%" if roe else "N/A")
                
                st.markdown("### Sensitivity / Sensibilité")
                df_sens = calculate_sensitivity_matrix(base_flow, assumptions, data['net_debt'], data['shares'])
                def color_coding(val):
                    color = 'red' if val < data['price'] else 'green'
                    return f'color: {color}; font-weight: bold'
                st.dataframe(df_sens.style.format("{:.2f}").applymap(color_coding), use_container_width=True)

            with tab3:
                st.subheader("Chart / Graphique")
                hist_chart = data['history'][['Close']].copy()
                if tech['sma_50'] is not None:
                     hist_chart['SMA 50'] = hist_chart['Close'].rolling(window=50).mean()
                     hist_chart['SMA 200'] = hist_chart['Close'].rolling(window=200).mean()
                st.line_chart(hist_chart)
                
                csv_data = hist_chart.to_csv().encode('utf-8')
                st.download_button("📥 CSV Download", csv_data, f'{ticker_input}_data.csv', 'text/csv')
                
                st.subheader("Comparables")
                peers_list = [p.strip() for p in assumptions['peers'].split(',')]
                comps = []
                comps.append({"Action": ticker_input, "P/E": data['pe_ratio'], "Beta": data['beta']})
                for p in peers_list:
                    try:
                        i = yf.Ticker(p).info
                        comps.append({"Action": p, "P/E": i.get('trailingPE'), "Beta": i.get('beta')})
                    except: pass
                st.dataframe(pd.DataFrame(comps), use_container_width=True)
        else:
            st.error(T['err_data'])
            
show_adsense_banner()
