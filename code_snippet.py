import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Analyze this startup:
Ambr AI	United Kingdom	HRtech	https://www.ambr.ai/  
"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""Here's a thinking process to generate the Ambr AI analysis:

1.  **Understand the Goal:** The user wants a detailed analysis of Ambr AI, a UK HRtech startup, following a specific 10-section structure. The analysis needs to be specific, actionable, data-driven (where possible), and consider the HRtech context.

2.  **Information Gathering Strategy:**
    *   **Primary Source:** The provided website (https://www.ambr.ai/) is the most crucial source. I need to thoroughly explore it, including the \"About Us,\" \"Product,\" \"Pricing,\" \"Blog,\" \"Case Studies\" (if any), and \"Contact\" pages.
    *   **Secondary Sources (via Search):** I need to use the search tool to find external information. Key areas to search for:
        *   Founder names and backgrounds.
        *   Funding rounds (amount, investors, dates).
        *   Team size and key hires.
        *   Competitors (direct and indirect).
        *   Market size data for HRtech, specifically employee engagement/wellbeing/AI coaching in the UK/Europe.
        *   News articles, press releases, reviews, or blog posts about Ambr AI.
        *   LinkedIn profiles for founders/key team members.
    *   **Search Queries (Initial Draft):**
        *   \"Who founded Ambr AI?\"
        *   \"Ambr AI funding rounds\"
        *   \"Ambr AI team size\"
        *   \"Ambr AI competitors\"
        *   \"HRtech market size UK employee engagement\"
        *   \"Ambr AI product features\"
        *   \"Ambr AI business model\"
        *   \"Reviews of Ambr AI platform\"
        *   \"Ambr AI news\"
        *   \"Ambr AI target market\"

3.  **Execute Search:** Run the planned search queries using the `google_search` tool.

4.  **Synthesize Information & Structure the Analysis:** Go through the 10 required sections and populate them based on information gathered from the website and search results.

    *   **1. Executive Summary:**
        *   *Core Business:* What does Ambr AI *do*? (Based on website headline/product description). Looks like AI-powered coaching for employee development and wellbeing.
        *   *Value Prop:* Why would a company buy this? (Benefits highlighted on the website – e.g., scalable coaching, improved engagement, retention, performance).
        *   *Stage:* Early stage? Seed? Pre-seed? (Look for funding info, team size, website maturity). Likely early stage.
        *   *Market Opp:* Is there a need for this? (Yes, employee wellbeing, engagement, and development are big HR trends. AI scalability is a key driver).

    *   **2. Founder & Team:**
        *   *Composition:* Find names (search results/website 'About Us'). Look for technical, business, HR expertise.
        *   *Strengths:* Based on backgrounds (e.g., prior startup experience, HR experience, AI/tech skills).
        *   *Development Areas:* What might be missing? (e.g., sales leadership if founders are purely technical, lack of deep HR domain expertise if purely tech, small team size). *Crucial to note if info is missing.*

    *   **3. Market Analysis:**
        *   *Target Market Size:* Search for HRtech market size, specifically coaching, employee engagement, L&D platforms in the UK/Europe. Note the methodology (e.g., TAM, SAM, SOM). Acknowledge potential data limitations for niche segments.
        *   *Competitors:* Identify direct (AI coaching platforms like BetterUp, CoachHub - though these might be larger scale, Ezra) and indirect (traditional coaching, L&D platforms, internal mentoring programs, performance management tools, wellbeing apps like Calm/Headspace for Business).
        *   *Position:* How does Ambr AI differentiate itself? (Focus on AI scalability, specific features, pricing, target segment - perhaps SMEs vs. enterprise?). Likely positioned as a scalable, potentially more affordable AI alternative/supplement to human coaching.
        *   *Growth Potential:* High, driven by AI adoption, focus on employee experience, remote work trends, and skills gaps.

    *   **4. Product/Solution:**
        *   *Core Features:* List specifics from the website (AI coaching conversations, goal setting, progress tracking, manager insights, integrations?).
        *   *Tech Innovation:* What's novel? (Proprietary AI models? Specific conversational AI approach? Integration capabilities? Data analytics?). Focus on the *AI* aspect.
        *   *Competitive Advantages:* Scalability, cost-effectiveness (vs. human coaches), accessibility (24/7), data insights, personalization potential.
        *   *Areas for Improvement:* Potential limitations? (Depth of coaching vs. humans, handling complex emotional issues, user adoption/engagement, integration breadth, proving ROI). *Note information gaps if specific features aren't detailed.*

    *   **5. Business Model:**
        *   *Revenue Streams:* Likely SaaS (Software as a Service). Tiered pricing based on users/features? Per-employee-per-month (PEPM)? (Check website 'Pricing' or infer).
        *   *Cost Structure:* Key costs? (R&D/Tech development, Sales & Marketing, Hosting/Infrastructure, Staff salaries, Customer Support).
        *   *Scalability:* High potential due to SaaS model and AI core. Low marginal cost per additional user once the platform is built.
        *   *Unit Economics:* Hard to know without internal data. Key metrics would be Customer Acquisition Cost (CAC), Customer Lifetime Value (CLTV), Churn Rate. Need to *estimate* or state the importance of these metrics. CLTV > CAC is essential.

    *   **6. Financial Situation:**
        *   *Funding Stage:* Search results are critical here. Pre-seed, Seed, Series A? Amount raised? Investors? Dates? *If no info found, state this clearly.*
        *   *Key Metrics:* (Likely not public). Mention key SaaS metrics: ARR/MRR, User Growth, Churn, CAC, CLTV, Burn Rate.
        *   *Resource Allocation:* Infer based on stage. Likely heavy on R&D and Product, followed by initial Sales & Marketing.
        *   *Health Indicators:* Based on funding, user growth (if mentioned anywhere), partnerships. *Lack of public data means this will be speculative.* State uncertainty.

    *   **7. Growth Strategy:**
        *   *Short-term:* Product refinement, acquiring early adopters/case studies, building brand awareness in the UK market, securing seed funding (if pre-seed).
        *   *Long-term:* Product expansion (more features, deeper integrations), international expansion (Europe first?), moving upmarket (larger enterprises?), developing stronger AI capabilities.
        *   *Market Expansion:* Geographic (UK -> Europe -> ?), Segment (SMEs -> Mid-market -> Enterprise?), Vertical (specific industries?).
        *   *Growth Levers:* Content marketing, partnerships (HR consultancies, other HRtech), direct sales, potentially freemium/trial models, demonstrating ROI.

    *   **8. Risk Assessment:**
        *   *Market:* Intense competition, slow adoption by target market, proving ROI of AI coaching, potential backlash against AI replacing human interaction.
        *   *Technical:* AI model effectiveness/bias, scalability issues, data security/privacy (GDPR crucial in UK/EU), integration challenges.
        *   *Operational:* Hiring talent, managing growth, customer support challenges, maintaining user engagement.
        *   *Mitigation:* Strong product differentiation, focus on data security/ethics, pilot programs to prove value, building a strong team, phased rollout, feedback loops.

    *   **9. SWOT Analysis:**
        *   *Strengths:* AI focus, scalability, potential cost-effectiveness, 24/7 availability, data insights, potentially niche focus (if identified). *Tie back to previous sections.*
        *   *Weaknesses:* Early stage, limited brand recognition/track record, potential user skepticism towards AI coaching, smaller team, reliance on funding. *Tie back to previous sections.*
        *   *Opportunities:* Growing demand for employee development/wellbeing, AI adoption in HR, remote work trends, potential partnerships, international expansion. *Tie back to Market Analysis/Growth.*
        *   *Threats:* Strong competition (established players, new entrants), economic downturn impacting HR budgets, data privacy regulations, slow market adoption, failure to prove ROI. *Tie back to Market/Risks.*

    *   **10. Recommendations:**
        *   *Strategic:* Focus on differentiating the AI (unique methodology, proven outcomes), build strong case studies early, clearly define target ICP (Ideal Customer Profile).
        *   *Resource Allocation:* Prioritize product development (esp. AI core & user experience) and securing initial referenceable customers. Balance R&D with targeted Sales/Marketing.
        *   *Risk Management:* Proactive GDPR compliance, transparent AI ethics policy, robust security measures, clear ROI metrics tracking for clients.
        *   *Growth Initiatives:* Content marketing focused on AI coaching benefits/ROI, strategic partnerships, pilot programs with key target clients. Consider a focused initial market segment (e.g., tech SMEs in the UK).

5.  **Refine and Review:**
    *   Read through the entire analysis.
    *   Ensure consistency between sections.
    *   Check for clarity, conciseness, and actionable insights.
    *   Explicitly state where information is missing or uncertain (e.g., specific funding details, internal metrics).
    *   Verify that all parts of the original prompt have been addressed.
    *   Format clearly with headings and bullet points.
    *   Add a disclaimer about information being based on publicly available data.

This structured approach ensures all required aspects are covered, leveraging available information while acknowledging gaps, and resulting in a comprehensive analysis."""),
                types.Part.from_text(text="""Okay, let's break down Ambr AI based on publicly available information.

**Disclaimer:** This analysis relies on information publicly available via the Ambr AI website and general web searches as of March 26, 2025. Access to internal data, specific financial metrics, or confidential strategic plans is not available, which limits the depth of certain sections.

**Note on Search Results & Disambiguation:** Several search results refer to \"Amber AI\" or \"Amber\" which are different companies (one in e-commerce/Amazon optimization, one in medical software, one an AI chatbot for employee engagement by inFeedo, one crypto/blockchain related). This analysis focuses *specifically* on **Ambr AI (ambr.ai)**, the UK-based HRtech startup focused on AI-driven workplace wellbeing and conversation simulation.

---

**1. EXECUTIVE SUMMARY**

*   **Core Business Description:** Ambr AI is a UK-based HRtech startup founded in 2022. It initially focused on using AI to analyze real-time workplace data (from tools like Slack, Teams, Outlook, Gmail) to identify root causes of employee stress and provide insights for improving wellbeing. More recently (based on their website), they seem to be pivoting or heavily emphasizing an AI platform for managers and employees to practice difficult workplace conversations using realistic voice simulations and receive AI-driven feedback.
*   **Key Value Proposition:**
    *   *Wellbeing Focus (Original/Data Analysis):* Proactively identify and mitigate workplace stress drivers using objective, passive data analysis rather than relying solely on surveys, aiming to reduce burnout, absenteeism, and attrition.
    *   *Conversation Practice Focus (Current Website):* Provide a safe, scalable, and private environment for employees (especially managers) to build confidence and competence in handling difficult conversations (e.g., feedback, conflict resolution) through realistic AI voice simulations and instant feedback.
*   **Current Stage of Development:** Early Stage. Founded in 2022, secured a £950K (~€1.1M) pre-seed round in late 2024. Team size is small (listed as 1-10 employees on some platforms). They have initial clients/case studies.
*   **Market Opportunity:** Significant. Addressing workplace stress/burnout and improving management/communication skills are major priorities for HR. The application of AI offers scalability and potentially lower costs compared to traditional methods (like human coaching or extensive L&D workshops). The UK HR tech market is valued at over £1 billion and growing, with high interest in AI solutions.

**2. FOUNDER & TEAM ASSESSMENT**

*   **Team Composition:**
    *   Co-founders: Zoe Stones (CEO), Jamie Wood, Steph Newton.
    *   Backgrounds: Combined experience from companies like Uber, Deloitte, Accenture, Spotify. This suggests a blend of tech, consulting, and potentially operational/product experience. Zoe Stones is listed as CEO.
*   **Key Strengths:**
    *   Relevant corporate experience at scale-ups and established firms.
    *   Early funding success indicates investor confidence in the team and vision.
    *   Focus on a clear pain point in HR (wellbeing/communication).
*   **Areas for Development:**
    *   Small team size (likely 1-10) may limit execution speed across product development, sales, and marketing.
    *   Specific deep HR domain expertise isn't explicitly highlighted (though consulting backgrounds may cover this).
    *   Scaling a sales function effectively as an early-stage startup.
    *   *Information Gap:* Detailed roles/expertise of Jamie Wood and Steph Newton aren't readily available from search results.

**3. MARKET ANALYSIS**

*   **Target Market Size:**
    *   The global HR Tech market was valued around $38 billion in 2023, projected to grow at a CAGR of ~9.3% to reach ~$84.7 billion by 2032.
    *   The UK HR Tech market is valued at over £1 billion and expected to grow, with ~60% of medium/large UK businesses using AI in HR/recruitment.
    *   The UK HR *analytics* market alone was valued at ~$200M in 2022, with a projected CAGR of 15%.
    *   Ambr AI targets a niche within this: AI for employee wellbeing analytics and/or AI for communication skills training. This specific niche size is hard to quantify but sits within large, growing markets (employee engagement, L&D, wellbeing). Initial focus seems UK-based, likely targeting mid-market to potentially larger enterprises, although SMEs are also a fast-growing segment for AI adoption in HR.
*   **Key Competitors:**
    *   *Wellbeing Analytics:* MoodConnect, Kaktus AI, Woba, Spring Health, Lyra Health, Headspace for Work (focus more on intervention but collect data), Visier (broader people analytics), potentially aspects of Qualtrics EX or Culture Amp.
    *   *AI Conversation Practice/Coaching:* Platforms potentially incorporating similar simulation features (though Ambr's voice AI focus might be specific), larger AI coaching platforms (BetterUp, CoachHub - though less focused on simulation), traditional L&D providers, internal training programs.
    *   *Specific named competitors:* BetterUp, TaskHuman, Cornerstone (in leadership/career coaching space where Ambr is listed as a 'Challenger' by CB Insights). Spring, Magellan Health, Thrive Global, AbleTo, Lyra Health, Headspace (as broader wellbeing platforms). Wellfound, Truework, Snoooz AI, JobKapture (listed as alternatives on G2, but seem less directly comparable based on product descriptions).
*   **Market Position:** Appears positioned as an innovative AI-first solution.
    *   For *wellbeing*, differentiation lies in passive data collection from existing tools vs. active surveys, aiming for objective, real-time insights into stress drivers.
    *   For *conversation practice*, differentiation lies in realistic voice AI simulation for safe practice and scalable skills development, potentially more cost-effective and accessible than human coaching/role-playing.
    *   Likely targeting tech-forward companies initially. CB Insights categorizes Ambr as a 'Challenger' in the leadership & career coaching space.
*   **Growth Potential:** High. Driven by:
    *   Increased corporate focus on employee wellbeing and mental health.
    *   Demand for effective and scalable management training.
    *   Growing acceptance and adoption of AI in HR functions.
    *   Potential cost and scalability advantages over traditional methods.

**4. PRODUCT/SOLUTION ANALYSIS**

*   **Core Features:**
    *   *Wellbeing Analytics (Based on funding news):* Integration with 50+ workplace tools (Slack, Teams, Google/Microsoft suites), passive data collection, AI/ML analysis of anonymized/aggregated data, identification of stress patterns/trends, tailored recommendations/insights for organizations.
    *   *Conversation Practice (Based on website):* Realistic voice AI conversation simulations, library of workplace scenarios (feedback, conflict, support, etc.), customizable scenarios, instant AI-generated feedback on communication skills. Mobile-friendly web application.
*   **Technical Innovation:**
    *   Proprietary AI/ML models for analyzing workplace communication/activity data for wellbeing insights (anonymized).
    *   Sophisticated conversational AI, specifically voice AI, designed to simulate realistic human interactions in workplace scenarios.
    *   Ability to integrate with a wide range of existing workplace tools (passive data collection aspect).
*   **Competitive Advantages:**
    *   *Scalability:* AI allows practice/analysis at a scale difficult/costly with humans.
    *   *Accessibility/Convenience:* 24/7 access for practice; passive data collection for insights without survey fatigue.
    *   *Objectivity (Potentially):* Data-driven insights rather than purely subjective survey responses (for wellbeing).
    *   *Safety:* Provides a safe space to practice difficult conversations without real-world consequences.
    *   *Cost-Effectiveness:* Likely lower cost per employee than extensive human coaching or workshops.
    *   *Data Insights:* Provides analytics on communication skills gaps or organizational stress drivers.
*   **Areas for Improvement:**
    *   *Product Focus Clarity:* Website heavily emphasizes conversation practice, while funding news highlights wellbeing analytics. Is it one product, two, or a pivot? This needs clarification.
    *   *AI Nuance:* AI may struggle with highly complex emotional nuance compared to a human coach/therapist. Ensuring the AI feedback is truly developmental is key.
    *   *Data Privacy/Ethics:* Heavy reliance on analyzing workplace data requires robust anonymization, transparency, and adherence to GDPR/privacy regulations to maintain employee trust. Clear communication on data usage is crucial.
    *   *Integration Depth:* Maintaining and expanding integrations is an ongoing effort.
    *   *Proving ROI:* Clearly demonstrating impact (reduced attrition, improved performance, lower stress levels) through client case studies will be critical.

**5. BUSINESS MODEL ANALYSIS**

*   **Revenue Streams:** Likely a B2B SaaS model.
    *   Pricing probably based on the number of users (e.g., per employee per month/year) or feature tiers.
    *   The website mentions flexible pricing based on requirements with volume discounts, requiring contact for a quote. This suggests value-based or enterprise-level pricing rather than simple self-serve tiers currently. Potential for add-on services like custom scenario development.
*   **Cost Structure:**
    *   *Primary Costs:* R&D (AI model development, platform engineering), Sales & Marketing, Cloud Hosting/Infrastructure (significant for AI processing), Personnel (salaries), Customer Support & Success.
    *   *Secondary Costs:* Office space (if any), compliance, administrative overhead.
*   **Scalability Potential:** High. Software and AI core are inherently scalable. Marginal costs per additional user should be relatively low once the platform is established, though AI computation costs can scale with usage.
*   **Unit Economics:**
    *   *Information Gap:* No public data on CAC (Customer Acquisition Cost), CLTV (Customer Lifetime Value), or Churn.
    *   *Key Considerations:* Need to ensure CLTV >> CAC. Factors influencing this include pricing, contract length, customer retention (churn rate), and upsell potential. Proving ROI (e.g., the claimed $500k savings for a 500-employee company) is key to justifying price and retaining clients.

**6. FINANCIAL SITUATION**

*   **Current Funding Stage:** Pre-Seed.
    *   Raised a total of £950K (~€1.1M) in a pre-seed round concluded around Sept/Oct 2024.
    *   Lead Investor: Fuel Ventures.
    *   Other Investors: Look AI Ventures, Loyal VC, SeedBlink, APX, Pi Labs, Veridian Ventures, Plug and Play.
*   **Key Financial Metrics:**
    *   *Information Gap:* No public information on MRR/ARR, burn rate, profitability, customer numbers (beyond a few named examples like Uber, BSC Consulting, Uplink).
    *   *Implied Metrics:* Based on client results cited (20% attrition drop, 40% stress absence drop), they are likely tracking these impact metrics closely for validation.
*   **Resource Allocation:**
    *   Given the recent funding and early stage, resources are likely prioritized towards:
        1.  Product Development: Enhancing AI capabilities (both analytics and conversation simulation), platform features, UI/UX.
        2.  Sales & Marketing: Acquiring initial customers, building brand awareness, developing case studies.
        3.  Team Expansion: Hiring key technical and potentially commercial roles.
*   **Financial Health Indicators:**
    *   Securing pre-seed funding from multiple VCs is a positive signal.
    *   Having notable clients like Uber suggests product validation.
    *   However, as an early-stage company, it is almost certainly pre-profitability and reliant on its funding runway. Financial health depends heavily on managing burn rate effectively while achieving growth milestones to secure future funding.

**7. GROWTH STRATEGY**

*   **Short-term Goals (Next 12-18 months):**
    *   Refine product based on early customer feedback (clarify focus between wellbeing analytics vs. conversation practice, or integrate them).
    *   Acquire more referenceable customers in the UK market.
    *   Develop strong case studies demonstrating ROI.
    *   Enhance AI capabilities (accuracy, predictive models for stress, realism in simulations).
    *   Potentially begin exploring adjacent European markets.
    *   Build out the core team.
*   **Long-term Vision:**
    *   Become a leading AI platform for employee development and wellbeing in the UK and Europe.
    *   Expand product suite (deeper analytics, broader range of skills training, integrations with performance management).
    *   Potentially move upmarket to serve larger enterprise clients more extensively.
    *   Revolutionize how companies approach employee wellbeing and skill development using AI.
*   **Market Expansion Plans:**
    *   Initial focus clearly on the UK.
    *   Logical next steps include English-speaking markets or nearby European countries (especially given EU investors like Look AI Ventures, SeedBlink).
    *   Segment expansion could involve targeting specific industries or moving from mid-market towards SMEs or larger enterprises depending on traction.
*   **Key Growth Levers:**
    *   Content Marketing: Educating HR leaders on AI benefits for wellbeing and skills.
    *   Direct Sales: Building relationships with target companies.
    *   Partnerships: Collaborating with HR consultancies, other HR tech vendors, potentially wellness providers.
    *   Product-Led Growth: Potentially offering trials or demos of the conversation simulator.
    *   Demonstrating ROI: Using client success data (attrition reduction, cost savings) as powerful sales tools.

**8. RISK ASSESSMENT**

*   **Market Risks:**
    *   *Competition:* Intense competition from established HRTech players and numerous startups in wellbeing, L&D, and AI coaching.
    *   *Market Adoption:* Potential skepticism or slow adoption of AI for sensitive areas like wellbeing analysis or conversation practice. HR budget constraints during economic downturns.
    *   *Proving Value:* Difficulty in definitively attributing ROI (e.g., reduced attrition) solely to Ambr AI's platform.
    *   *Product-Market Fit Evolution:* Ensuring the product continues to meet evolving customer needs, especially if pivoting/refining focus.
*   **Technical Risks:**
    *   *AI Accuracy & Bias:* Ensuring AI models (for analysis and conversation) are accurate, fair, and unbiased. Poor performance erodes trust.
    *   *Data Security & Privacy:* Handling sensitive employee data requires robust security and strict GDPR compliance. A breach would be catastrophic.
    *   *Scalability:* Ensuring the platform can handle growth in users and data volume reliably.
    *   *Integration Reliability:* Maintaining stable integrations with dozens of third-party tools.
*   **Operational Risks:**
    *   *Talent Acquisition:* Attracting and retaining skilled AI/ML engineers, product managers, and sales talent in a competitive market.
    *   *Execution Risk:* Ability of a small team to effectively execute product development, sales, and support simultaneously.
    *   *Customer Churn:* Failing to retain customers if the product doesn't deliver expected value or if user engagement drops off.
*   **Mitigation Strategies:**
    *   *Differentiation:* Clearly articulate unique value proposition (e.g., passive data, voice AI realism).
    *   *Transparency & Ethics:* Proactive communication about data usage, anonymization, and AI limitations. Strong focus on GDPR.
    *   *Pilot Programs:* Use pilots to demonstrate value and gather feedback in lower-risk settings for clients.
    *   *Robust Engineering & Security:* Invest heavily in secure architecture and reliable AI development.
    *   *Focus:* Prioritize key features and target customer segments rather than trying to do everything at once.
    *   *Customer Success:* Invest in onboarding and support to ensure clients achieve value.

**9. SWOT ANALYSIS**

*   **Strengths:**
    *   Innovative AI-driven approach (both passive data analysis and voice simulation).
    *   Addresses critical HR needs (wellbeing, communication skills).
    *   Scalable technology core.
    *   Secured pre-seed funding from reputable VCs.
    *   Experienced founding team from relevant backgrounds.
    *   Early client validation (e.g., Uber).
*   **Weaknesses:**
    *   Early stage with limited market presence and brand recognition.
    *   Small team size potentially constraining growth.
    *   Potential ambiguity in primary product focus (wellbeing analytics vs. conversation practice).
    *   Reliance on external funding.
    *   Proving definitive ROI can be challenging.
    *   Potential employee resistance/skepticism towards AI monitoring or coaching.
*   **Opportunities:**
    *   Growing market demand for HR tech, AI solutions, employee wellbeing, and L&D.
    *   Expansion into new geographic markets (Europe).
    *   Partnerships with complementary service providers (consultants, other HR tech).
    *   Developing deeper predictive capabilities for wellbeing.
    *   Expanding scenario library and customization for conversation practice.
    *   Targeting specific industry verticals with tailored solutions.
*   **Threats:**
    *   Intense competition from larger, better-funded players and new entrants.
    *   Economic downturns impacting HR budgets.
    *   Stricter data privacy regulations or negative public perception of AI in the workplace.
    *   Failure to keep pace with rapid AI advancements.
    *   Inability to demonstrate clear, quantifiable ROI to customers.
    *   Potential for AI models to exhibit bias or inaccuracies.

**10. RECOMMENDATIONS**

*   **Strategic Priorities:**
    *   **Clarify Product Focus:** Sharpen the primary value proposition and messaging. Is it an integrated platform, or are the wellbeing analytics and conversation practice distinct offerings? Ensure marketing and product development are aligned.
    *   **Build Strong Case Studies:** Focus intensely on early customers to generate compelling, quantifiable results (ROI, engagement uplift, skill improvement, stress reduction). Use these for validation and marketing.
    *   **Define Ideal Customer Profile (ICP):** Double down on the specific type of company (size, industry, culture) where Ambr AI provides the most value and gain traction there first.
    *   **Prioritize Trust & Ethics:** Be exceptionally transparent about data usage, anonymization, and AI limitations. Make GDPR compliance and ethical AI a core tenet.
*   **Resource Allocation:**
    *   **Product:** Continue investing in AI R&D (model accuracy, realism, insights) and user experience. Ensure platform stability and scalability.
    *   **Sales & Marketing:** Focus on building a pipeline within the defined ICP. Leverage content marketing and case studies. Invest in a small, effective sales team or process.
    *   **Customer Success:** Ensure early customers are successful and become advocates. Feedback loops are critical.
*   **Risk Management:**
    *   **Data Privacy:** Continuous audits and adherence to best practices for GDPR and data security. Clear internal policies and external communication.
    *   **AI Bias:** Implement processes for monitoring and mitigating bias in AI models.
    *   **Market Education:** Proactively address potential skepticism about AI through thought leadership and clear benefit communication.
    *   **Financial:** Maintain strict burn rate control and focus on milestones needed for the next funding round.
*   **Growth Initiatives:**
    *   **Targeted Pilots:** Offer structured pilot programs to key prospects within the ICP to demonstrate value quickly.
    *   **Strategic Partnerships:** Explore partnerships with HR consultants or complementary tech platforms that reach the target audience.
    *   **Content Marketing:** Create valuable content (blogs, webinars, whitepapers) around AI in HR, workplace stress, communication skills, demonstrating thought leadership.
    *   **Iterative Development:** Maintain agile development practices to respond quickly to customer feedback and market changes.

This analysis provides a snapshot based on available data. A deeper understanding would require access to internal company information."""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(google_search=types.GoogleSearch())
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=65536,
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""Please analyze Ambr AI (https://www.ambr.ai/), a UK-based HRtech startup. Provide a detailed analysis following this structure:

1. EXECUTIVE SUMMARY
- Core Business Description
- Key Value Proposition
- Current Stage of Development
- Market Opportunity

2. FOUNDER & TEAM ASSESSMENT
- Team Composition
- Key Strengths
- Areas for Development

3. MARKET ANALYSIS
- Target Market Size
- Key Competitors
- Market Position
- Growth Potential

4. PRODUCT/SOLUTION ANALYSIS
- Core Features
- Technical Innovation
- Competitive Advantages
- Areas for Improvement

5. BUSINESS MODEL ANALYSIS
- Revenue Streams
- Cost Structure
- Scalability Potential
- Unit Economics

6. FINANCIAL SITUATION
- Current Funding Stage
- Key Financial Metrics
- Resource Allocation
- Financial Health Indicators

7. GROWTH STRATEGY
- Short-term Goals
- Long-term Vision
- Market Expansion Plans
- Key Growth Levers

8. RISK ASSESSMENT
- Market Risks
- Technical Risks
- Operational Risks
- Mitigation Strategies

9. SWOT ANALYSIS
- Core Strengths
- Primary Weaknesses
- Key Opportunities
- Critical Threats

10. RECOMMENDATIONS
- Strategic Priorities
- Resource Allocation
- Risk Management
- Growth Initiatives

For each section:
- Provide specific, actionable insights
- Include relevant metrics and data points where available
- Highlight any information gaps or uncertainties
- Consider the HRtech industry context
- Focus on practical implications"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
