from model import QueryService 
import asyncio

async def invoke_flow(text: str):
    print(text)
    service = QueryService()
    service.query_raw( text)

    parsed_input_as_json = service.json
    startup_name = parsed_input_as_json.get("startup_name", "Unkonwn")


    manual_enrichment = ""
    web_search_results = ""

    autumated_enrichment_websearch_prompt = f"""
    Some information below was extracted from a startup description, from {startup_name}.
    Additional information has been manually enriched and retrieved through web search.

    Your task:
    - If any field in the parsed data is marked as "Not found", try to intelligently infer the missing information using all available context.
    - If you still cannot confidently determine the missing information, reply with "Unknown".
    - Use only the provided context; do not make assumptions beyond what is given.

    Context sections:
    - Parsed Input:
    {parsed_input_as_json}

    - Manual Enrichment:
    {manual_enrichment}

    - Web Search Results:
    {web_search_results}

    Respond only in this JSON format:
    {{
    "startup_name": "...",
    "founders": ["...", "..."]
    }}
    """
    context_text_from_automated_enrichment = await service.query(autumated_enrichment_websearch_prompt, autumated_enrichment_websearch_prompt)

    service_json = service.json
    founders = service_json.get("founders", "Unknown")

    specialized_enrichment_prompt_1 = f"""
    You are an expert startup analyst.

    Based on the information below, find and summarize key details about the startup {startup_name}:
    - What product or service do they offer?
    - What is their business model (how do they make money)?
    - What traction do they have (revenue, user growth, partnerships, clients)?
    - Who are their competitors?
    - Have they raised funding? If yes, from whom, how much, and when?

    Information:
    {context_text_from_automated_enrichment}

    Respond in a clean structured bullet point format. Use the websearch to find the information if you need to.
    Return this JSON format:
    {{
    "summary": "...",
    "pre_scores": {{
        "product_score": 0-10,
        "traction_score": 0-10
    }},
    "justification": {{
        "product_score": "...",
        "traction_score": "..."
    }}
    }}
    """

    specialized_enrichment_prompt_2 = f"""
    You are researching startup founders.

    Based on the information below, find and summarize key details about the founders {founders}.
    For each founder, find:
    - Education background
    - Professional experience (previous startups, notable companies)
    - Expertise in the startup’s domain
    - Past entrepreneurial successes or failures

    Information:
    {context_text_from_automated_enrichment}

    Respond founder by founder in a clean structured format. Use the websearch to find the information if you need to.
    Return this JSON format:
    {{
    "founder_insights": "...",
    "pre_scores": {{
        "team_score": 0-10
    }},
    "justification": {{
        "team_score": "..."
    }}
    }}
    """
    specialized_enrichment_prompt_3 = f"""
    You are analyzing the market for a startup named {startup_name}.

    Based on the information below, find and summarize:
    - The total addressable market (TAM) for their product/service
    - Market growth trends
    - Major risks and challenges they might face (regulatory, technological, competitive)
    - Emerging opportunities they could exploit

    Information:
    {context_text_from_automated_enrichment}

    Respond in a clean structured bullet point format. Use the websearch to find the information if you need to.
    Return this JSON format:
    {{
    "market_insights": "...",
    "pre_scores": {{
        "market_score": 0-10,
        "risk_score": 0-10
    }},
    "justification": {{
        "market_score": "...",
        "risk_score": "..."
    }}
    }}
    """

    specialized_text_1 = await service.query(specialized_enrichment_prompt_1, additional_info= " ")
    specialized_text_2 = await service.query( specialized_enrichment_prompt_2, additional_info= " ")
    specialized_text_3 = await service.query( specialized_enrichment_prompt_3, additional_info= " ")

    aggregated_text = f"""
    {context_text_from_automated_enrichment}
    
    compare the following information (if also appears in the previous one) with the previous one and prioritize the previous one:

    {specialized_text_1}
    {specialized_text_2}
    {specialized_text_3}
    """

    specialized_enrichment_prompt_4 = f"""
    You are a research assistant for a venture capital firm.

    Your task is to search social media platforms (e.g., LinkedIn, Twitter/X, Instagram, TikTok) to gather useful insights about a startup's public presence and activity. 
    Focus only on *business-relevant* content. Avoid random or irrelevant posts.

    Startup: "{startup_name}"
    Founders: "{founders}"

    Your goal is to collect and summarize the following:
    1. **Official Presence**: Do they have verified or active official accounts? Provide links.
    2. **Content Activity**: Are they posting regularly? What type of content (e.g., product updates, hiring, customer success, thought leadership)?
    3. **Engagement Level**: Do their posts get likes, comments, shares? Give an estimate (low, medium, high).
    4. **Audience Type**: Who engages with their content? Customers, developers, investors, general public?
    5. **Tone & Branding**: What's the general tone? Professional, playful, technical, community-driven?
    6. **Notable Mentions**: Any press, viral content, partnerships, or influencers talking about them?
    7. **Potential Red Flags**: Any controversies, backlash, customer complaints, or spammy practices?

    Only use publicly available information. Be concise but informative.

    Respond in this JSON format:
    {{
    "official_accounts": {{
        "linkedin": "...",
        "twitter": "...",
        "instagram": "...",
        "other": "..."
    }},
    "content_summary": "...",
    "engagement_level": "...",
    "audience_type": "...",
    "tone_and_branding": "...",
    "notable_mentions": "...",
    "red_flags": "...",
    "social_media_summary": "...",
    "pre_scores": {{
        "traction_score": 0-10,
        "risk_score": 0-10
    }},
    "justification": {{
        "traction_score": "...",
        "risk_score": "..."
    }}
    }}
    """

    text_for_truncation_score = await service.query(specialized_enrichment_prompt_4, additional_info= " ")


    #TODO: give these examples specific scores, so we can use them to calibrate the model
    failed_examples = """
    1. MySpace: Failed to adapt to rising competitors like Facebook.
    2. Friendster: Early to market but failed to scale and retain users.
    3. Vine: Lost user engagement, eventually shut down.
    4. Zapstream: Lacked traction despite live-streaming focus.
    5. Dodgeball: Ahead of its time but unfriendly UX and poor ecosystem.
    6. Chef'd: Sudden shutdown despite growth, issues with sustainability.
    7. Secret: Anonymous social network, couldn’t maintain long-term value.
    8. Gowalla: Lost out to more polished competitor (Foursquare).
    9. ArgyleSocial: Failed to secure market traction.
    10. Dopplr: Travel startup that never reached mainstream scale.
    """

    successful_examples = """
    - Snowflake: Cloud-native data warehouse that scaled efficiently; innovative architecture; strong team.
    - DoorDash: Solved a real need, saw explosive growth especially during the pandemic; IPO success.
    - Zoom: Great timing, perfect product-market fit, massive pandemic growth; easy UX.
    - Beyond Meat: Innovated in food, strong distribution, mainstream consumer adoption.
    - Robinhood: Disrupted finance with commission-free trading; viral growth; appealed to new investor generation.
    - Palantir: Deep tech with strong B2B/Gov traction; long-term contracts and strategic expansion.
    - Stripe: Dev-friendly infrastructure; scaled globally; strong partnerships.
    - SpaceX: Repeated technical innovation and delivery; long-term vision and execution.
    - Uber: Disrupted transportation globally; diversified offerings and scaled rapidly.
    - Airbnb: Democratized travel; great timing and product-market fit.
    """

    evaluation_prompt = f"""
    You are a professional venture capitalist evaluating a startup named {startup_name}, the founder(s) is(are) {founders}.

    You have seen many real-world examples of both successful and failed startups.
    Use the following examples to calibrate your evaluation:

    Examples of Failed Startups, that gets a very low score 1:
    {failed_examples}

    Examples of Successful Startups, that get a very high score 10:
    {successful_examples}

    Now, based solely on the information below — even if some fields are marked as "Not found" or "Unknown" — assign the following scores from 0 to 10:
    - Team Score: Strength and experience of the founders
    - Market Score: Size and growth potential of the market
    - Product Score: Quality, innovation, and differentiation of the product
    - Traction Score: Revenue, user growth, partnerships, or funding milestones, consider also the social media presence here the info: {text_for_truncation_score}
    - Risk Score: Estimated risk level (lower score means lower risk)

    Important:
    - Do not assume any missing information. If a detail is marked as "Not found" or "Unknown", lower the score appropriately and explain it.
    - Only use what is present in the text. No external research or guessing.
    - Base the Final Overall Score on the provided scores, adjusting slightly if necessary.

    After assigning scores, provide:
    - A justification for each score, explaining your reasoning and how you came to the score.
    - A Final Overall Score
    - A final 4–6 sentence summary giving an overall assessment of the startup’s potential and main concerns

    Information:
    {aggregated_text}

    You must use the scores provided in the previous Inforamtion text to guide and calibrate your final evaluation, not override them. You can adjust slightly based on deeper insight.

    "Any time you finish your search, you MUST output a single JSON object "
    "and nothing else.  "
    "Your JSON MUST match the schema:\n"
    {{
    company_info: {{
    "company_name": "...",
    "founder_name": "...",
    funding_stage: "...",
    funding_amount: "...",
    growth_rate: "",
    product_stage: "...",
    founding year: "...",
    competitors: "...",}},
    "team_score": ...,
    "market_score": ...,
    "product_score": ...,
    "traction_score": ...,
    "risk_score": ...,
    "overall_score": ...,
    "justifications": {{
        "team_score": "...",
        "market_score": "...",
        "product_score": "...",
        "traction_score": "...",
        "risk_score": "...",
        "overall_score": "..."
    }},
    "summary": "..."
    }}
    """

    find_logo = f"""
    You are a professional Logo finder, that scours the web for startup logos.
    Your task is to find the logo of the startup {startup_name} and provide a link to it.
    If you cannot find the logo, provide a link to the first google image result for the startup name.
    It is paramount that the url works. it must be a direct image link and not a link to a website.
    You can use any search engine you want, but you must provide a link to the image.

    Any time you finish your search, you MUST output a single JSON object "
    and nothing else.  "
    Your JSON MUST match the schema:\n"
    "{{ url: "...."}}"

    Example:
    {{
    "url": "https://example.com/logo.png"
    }}
    """

    service.query_raw(evaluation_prompt, additional_info= " ")
    temp_json = service.json
    await service.query(find_logo, additional_info= " ")
    logo_json = service.json
    logo_url = logo_json.get("url", "Unknown")
    # Combine logo_json with temp_json into one single JSON
    combined_json = {**temp_json, "logo_url": logo_url}

    print("Combined JSON:", combined_json)

    return combined_json

if __name__ == "__main__":
    company = "Uber"  
    text = f"You are a competent Analyst that scouts for startup companies. I need you to evaluate the startup company {company}. I need you to give a final verdict with a detailed report on them and how you would value them as a company. Start what should be said to the user with FINAL_RESULT. You may check the online sources. I need especially the following information: 1) What is the company doing? 2) How are they doing it? 3) How are they different from their competitors? 4) What is their business model? 5) What is their target market? 6) What is their current valuation? 7) What are their future plans? 8) What are the risks associated with this company? 9) What is your final verdict on this company? Give me also the KPI's of their: growth rate, product stage, revenue growth, funding stage, and amount. You need to dig deep.  You should only retrieve this information from the following parsed pdf file;"
    asyncio.run(invoke_flow(text))