"""IAB Content Taxonomy 3.0 — reference data used as a cached system-prompt prefix."""

IAB_TAXONOMY_TEXT = """
## IAB Content Taxonomy 3.0 — Reference

Use the codes and names below when categorising audience segments. Always cite Tier 1 ID,
Tier 1 Name, Tier 2 ID, and Tier 2 Name. Where no exact Tier 2 match exists, use the
closest parent and note it.

---

### Tier 1: Automotive (IAB2)
IAB2-1  Auto Parts
IAB2-2  Auto Repair
IAB2-3  Buying/Selling Cars
IAB2-4  Car Culture
IAB2-5  Certified Pre-Owned
IAB2-6  Convertible
IAB2-7  Coupe
IAB2-8  Crossover / SUV
IAB2-9  Diesel
IAB2-10 Electric Vehicle (EV)
IAB2-11 Hatchback
IAB2-12 Hybrid / Plug-In Hybrid
IAB2-13 Luxury / Premium Vehicles
IAB2-14 Minivan
IAB2-15 Motorcycles
IAB2-16 Off-Road / Adventure Vehicles
IAB2-17 Performance / Sports Cars
IAB2-18 Pickup Truck
IAB2-19 Roadside Assistance
IAB2-20 Sedan
IAB2-21 Trucks & Accessories
IAB2-22 Vintage Cars
IAB2-23 Wagon
IAB2-24 Van

### Tier 1: Business and Finance (IAB3)
IAB3-1  Advertising / Marketing
IAB3-2  Agriculture
IAB3-3  Biotech / Biomedical
IAB3-4  Business Software / SaaS
IAB3-5  Construction
IAB3-6  Forestry
IAB3-7  Government / Public Sector
IAB3-8  Green / Sustainable Business
IAB3-9  Human Resources / Hiring
IAB3-10 Logistics / Supply Chain
IAB3-11 Manufacturing
IAB3-12 Metals / Mining
IAB3-13 Mergers & Acquisitions
IAB3-14 Small Business
IAB3-15 Startups / Entrepreneurship

### Tier 1: Careers (IAB4)
IAB4-1  Career Planning
IAB4-2  College / Higher Education
IAB4-3  Financial Aid / Scholarships
IAB4-4  Job Fairs
IAB4-5  Job Search / Recruitment
IAB4-6  Resume / CV Writing
IAB4-7  Nursing / Healthcare Careers
IAB4-8  Telecommuting / Remote Work
IAB4-9  Military / Veterans Careers
IAB4-10 Trade / Vocational Training

### Tier 1: Education (IAB5)
IAB5-1  7-12 Education
IAB5-2  Adult Education / Continuing Learning
IAB5-3  Art History
IAB5-4  College Administration
IAB5-5  College Life
IAB5-6  Distance Learning / Online Courses
IAB5-7  English as a Second Language
IAB5-8  Graduate School
IAB5-9  Homeschooling
IAB5-10 Homework / Study Tips
IAB5-11 K-6 Educators
IAB5-12 Language Learning
IAB5-13 Private School
IAB5-14 Special Education
IAB5-15 Standardised Testing / Tutoring
IAB5-16 STEM Education

### Tier 1: Events and Attractions (IAB6)
IAB6-1  Amusement Parks
IAB6-2  Concerts / Music Festivals
IAB6-3  Sporting Events (Live)
IAB6-4  Conventions / Expos / Trade Shows
IAB6-5  Fairs / Carnivals
IAB6-6  Film Festivals
IAB6-7  Food & Drink Festivals
IAB6-8  Holiday Events / Seasonal Celebrations
IAB6-9  Museums / Galleries
IAB6-10 Theatre / Performing Arts
IAB6-11 Tourism Attractions

### Tier 1: Family and Relationships (IAB7)
IAB7-1  Dating / Romance
IAB7-2  Divorce Support
IAB7-3  Eldercare
IAB7-4  Family Internet
IAB7-5  Parenting / Family Life
IAB7-6  Pregnancy / Maternity
IAB7-7  Same-Sex Relationships
IAB7-8  Weddings / Anniversaries
IAB7-9  Children's Education
IAB7-10 Stay-at-Home Parents

### Tier 1: Food and Drink (IAB8)
IAB8-1  American Cuisine
IAB8-2  Barbecues / Grilling
IAB8-3  Cajun / Creole
IAB8-4  Chinese Cuisine
IAB8-5  Cocktails / Beer / Wine
IAB8-6  Coffee / Tea
IAB8-7  Cuisine Topics
IAB8-8  Desserts / Baking
IAB8-9  Dining Out / Restaurants
IAB8-10 Food Allergies / Dietary Restrictions
IAB8-11 French Cuisine
IAB8-12 Health / Low-Fat Cooking
IAB8-13 Italian Cuisine
IAB8-14 Japanese Cuisine / Sushi
IAB8-15 Mexican Cuisine
IAB8-16 Vegan / Plant-Based Diet
IAB8-17 Vegetarian / Organic
IAB8-18 World Cuisines

### Tier 1: Healthy Living (IAB10)
IAB10-1 Exercise / Fitness
IAB10-2 A.D.D.
IAB10-3 AIDS/HIV
IAB10-4 Allergies
IAB10-5 Alternative Medicine
IAB10-6 Arthritis
IAB10-7 Asthma
IAB10-8 Autism / PDD
IAB10-9 Bipolar Disorder
IAB10-10 Brain Tumor
IAB10-11 Cancer
IAB10-12 Cholesterol
IAB10-13 Chronic Pain
IAB10-14 Cold & Flu
IAB10-15 Deafness
IAB10-16 Dental Care
IAB10-17 Depression
IAB10-18 Dermatology
IAB10-19 Diabetes
IAB10-20 Epilepsy
IAB10-21 GERD / Acid Reflux
IAB10-22 Headache / Migraines
IAB10-23 Heart Disease
IAB10-24 Herbs / Supplements
IAB10-25 Holistic Healing
IAB10-26 IBS / Crohn's Disease
IAB10-27 Incest / Abuse Support
IAB10-28 Incontinence
IAB10-29 Infertility
IAB10-30 Men's Health
IAB10-31 Nutrition
IAB10-32 Orthopedics
IAB10-33 Panic / Anxiety Disorders
IAB10-34 Pediatrics
IAB10-35 Physical Therapy
IAB10-36 Psychology / Psychiatry
IAB10-37 Senior Health
IAB10-38 Sexuality
IAB10-39 Sleep Disorders
IAB10-40 Smoking Cessation
IAB10-41 Substance Abuse
IAB10-42 Thyroid Disease
IAB10-43 Weight Loss
IAB10-44 Women's Health
IAB10-45 Mental Health & Wellness
IAB10-46 Fitness Wearables / Health Tech

### Tier 1: Hobbies and Interests (IAB11)
IAB11-1 Art / Technology
IAB11-2 Arts & Crafts
IAB11-3 Beadwork
IAB11-4 Birdwatching
IAB11-5 Board Games / Puzzles
IAB11-6 Candle & Soap Making
IAB11-7 Card Games
IAB11-8 Chess
IAB11-9 Cigars
IAB11-10 Collecting
IAB11-11 Comic Books
IAB11-12 Drawing / Sketching
IAB11-13 Freelance Writing
IAB11-14 Genealogy / Ancestry
IAB11-15 Getting Published
IAB11-16 Guitar
IAB11-17 Home Recording
IAB11-18 Investors & Patents
IAB11-19 Jewelry Making
IAB11-20 Magic & Illusion
IAB11-21 Needlework
IAB11-22 Painting
IAB11-23 Photography
IAB11-24 Radio
IAB11-25 Roleplaying Games
IAB11-26 Sci-Fi & Fantasy
IAB11-27 Scrapbooking
IAB11-28 Screenwriting
IAB11-29 Stamps & Coins
IAB11-30 Video & Computer Games
IAB11-31 Woodworking

### Tier 1: Home and Garden (IAB12)
IAB12-1 Appliances
IAB12-2 Entertaining / Hosting
IAB12-3 Environmental Safety
IAB12-4 Gardening
IAB12-5 Home Repair / DIY
IAB12-6 Home Theater
IAB12-7 Interior Decorating / Design
IAB12-8 Landscaping
IAB12-9 Remodeling & Construction
IAB12-10 Smart Home / Connected Devices
IAB12-11 Sustainability / Green Living

### Tier 1: Movies (IAB14)
IAB14-1 Action & Adventure Films
IAB14-2 Animation Films
IAB14-3 Blockbusters / New Releases
IAB14-4 Bollywood / World Cinema
IAB14-5 Comedy Films
IAB14-6 Documentary Films
IAB14-7 Drama / Awards Season
IAB14-8 Horror / Thriller Films
IAB14-9 Kids & Family Films
IAB14-10 Sci-Fi / Fantasy Films
IAB14-11 Streaming / OTT

### Tier 1: Music and Audio (IAB15)
IAB15-1 Adult Contemporary
IAB15-2 Bluegrass
IAB15-3 Blues
IAB15-4 Classical Music
IAB15-5 Country Music
IAB15-6 EDM / Dance Music
IAB15-7 Gospel / Religious Music
IAB15-8 Hip-Hop / R&B
IAB15-9 Indie / Alternative
IAB15-10 Jazz
IAB15-11 Latin Music
IAB15-12 Metal / Hard Rock
IAB15-13 Music Equipment
IAB15-14 Music Festivals
IAB15-15 New Age
IAB15-16 Opera
IAB15-17 Pop Music
IAB15-18 Rock Music
IAB15-19 Songwriting / Production
IAB15-20 Podcasts / Audio

### Tier 1: News and Politics (IAB16)
IAB16-1 Elections / Voting
IAB16-2 Gossip / Celebrity News
IAB16-3 International News
IAB16-4 Local News
IAB16-5 National News
IAB16-6 Politics
IAB16-7 Weather
IAB16-8 US Congress
IAB16-9 White House / Presidential News

### Tier 1: Personal Finance (IAB17)
IAB17-1 Beginning Investing
IAB17-2 Credit / Debt & Loans
IAB17-3 Financial News
IAB17-4 Financial Planning
IAB17-5 Hedge Fund
IAB17-6 Insurance
IAB17-7 Investing
IAB17-8 Mutual Funds
IAB17-9 Options
IAB17-10 Retirement Planning
IAB17-11 Stocks
IAB17-12 Tax Planning
IAB17-13 Cryptocurrency / Digital Assets
IAB17-14 Mortgages / Home Loans
IAB17-15 BNPL / Fintech

### Tier 1: Real Estate (IAB20)
IAB20-1 Apartments / Rentals
IAB20-2 Architects
IAB20-3 Buying a Home
IAB20-4 Selling a Home
IAB20-5 Commercial Real Estate
IAB20-6 Foreclosures
IAB20-7 Luxury Real Estate
IAB20-8 Mortgage / Home Finance (see IAB17-14)
IAB20-9 Real Estate Investing
IAB20-10 Vacation Properties / Short-Term Rental

### Tier 1: Science (IAB22)
IAB22-1 Astrology
IAB22-2 Biology
IAB22-3 Chemistry
IAB22-4 Geology
IAB22-5 Paranormal Phenomena
IAB22-6 Physics
IAB22-7 Space / Astronomy
IAB22-8 Weather / Climate
IAB22-9 Artificial Intelligence / ML
IAB22-10 Climate Change / Environment

### Tier 1: Shopping (IAB23)
IAB23-1 Couponing / Deal Hunting
IAB23-2 Comparison Shopping
IAB23-3 Contests & Freebies
IAB23-4 Engines / Aggregators
IAB23-5 Gift Guides / Registry
IAB23-6 Holiday Shopping
IAB23-7 Luxury Goods
IAB23-8 Online Auctions
IAB23-9 Online Shopping / E-Commerce
IAB23-10 Retail / Department Stores

### Tier 1: Sports (IAB24)
IAB24-1 Auto Racing / Motorsports
IAB24-2 Baseball / MLB
IAB24-3 Bicycling
IAB24-4 Bodybuilding
IAB24-5 Boxing / MMA
IAB24-6 Canoeing / Kayaking
IAB24-7 Cheerleading
IAB24-8 Climbing
IAB24-9 Cricket
IAB24-10 Figure Skating / Winter Sports
IAB24-11 Fly Fishing
IAB24-12 Football / NFL / NCAA
IAB24-13 Freshwater Fishing
IAB24-14 Game & Fish
IAB24-15 Golf
IAB24-16 Horse Racing
IAB24-17 Horses
IAB24-18 Hunting / Shooting
IAB24-19 Inline Skating / Skateboards
IAB24-20 Martial Arts
IAB24-21 Mountain Biking
IAB24-22 NASCAR Racing
IAB24-23 Olympics / World Games
IAB24-24 Paintball
IAB24-25 Power & Motorcycles
IAB24-26 Basketball / NBA / NCAA
IAB24-27 Ice Hockey / NHL
IAB24-28 Rodeo
IAB24-29 Rugby
IAB24-30 Running / Jogging
IAB24-31 Sailing
IAB24-32 Saltwater Fishing
IAB24-33 Scuba Diving
IAB24-34 Skateboarding
IAB24-35 Skiing / Snowboarding
IAB24-36 Snowmobiles
IAB24-37 Soccer / MLS / International Football
IAB24-38 Softball
IAB24-39 Swimming / Aquatics
IAB24-40 Table Tennis / Ping Pong
IAB24-41 Tennis
IAB24-42 Volleyball
IAB24-43 Walking
IAB24-44 Waterski / Wakeboard
IAB24-45 Fantasy Sports / Sports Betting
IAB24-46 Esports
IAB24-47 Pickleball

### Tier 1: Style and Fashion (IAB25)
IAB25-1 Beauty
IAB25-2 Body Art / Tattoos
IAB25-3 Clothing
IAB25-4 Fashion Design
IAB25-5 Jewelry
IAB25-6 Accessories
IAB25-7 Men's Fashion
IAB25-8 Women's Fashion
IAB25-9 Sustainable / Slow Fashion
IAB25-10 Sneakers / Streetwear

### Tier 1: Technology and Computing (IAB26)
IAB26-1 3D Graphics
IAB26-2 Animation
IAB26-3 Antivirus / Security Software
IAB26-4 C/C++
IAB26-5 Cameras & Camcorders
IAB26-6 Cell Phones / Smartphones
IAB26-7 Computer Certification
IAB26-8 Computer Networking
IAB26-9 Computer Peripherals
IAB26-10 Computer Reviews
IAB26-11 Data Centers
IAB26-12 Databases
IAB26-13 Desktop Publishing
IAB26-14 Desktop Video
IAB26-15 Email
IAB26-16 Graphics Software
IAB26-17 Home Video / DVD
IAB26-18 Internet Technology
IAB26-19 Java
IAB26-20 JavaScript
IAB26-21 Mac Support
IAB26-22 MP3 / MIDI
IAB26-23 Net Conferencing
IAB26-24 Net for Beginners
IAB26-25 Network Security
IAB26-26 Palmtops / PDAs
IAB26-27 PC Support
IAB26-28 Portable Entertainment
IAB26-29 Shareware / Freeware
IAB26-30 Unix
IAB26-31 Visual Basic
IAB26-32 Web Clip Art
IAB26-33 Web Design/HTML
IAB26-34 Web Search
IAB26-35 Windows
IAB26-36 Artificial Intelligence / LLMs
IAB26-37 Cloud Computing / SaaS
IAB26-38 Cybersecurity / Privacy
IAB26-39 Wearable Technology
IAB26-40 AR / VR / XR

### Tier 1: Television (IAB27)
IAB27-1 Animation / Anime
IAB27-2 Broadcast / Network TV
IAB27-3 Cable TV
IAB27-4 Classic TV
IAB27-5 Drama / Soap Operas
IAB27-6 News / Current Affairs TV
IAB27-7 Reality TV
IAB27-8 Science Fiction / Fantasy TV
IAB27-9 Sports TV
IAB27-10 Streaming / OTT Services
IAB27-11 TV Awards / Events

### Tier 1: Travel (IAB28)
IAB28-1 Adventure Travel
IAB28-2 Africa Travel
IAB28-3 Air Travel
IAB28-4 Australia & New Zealand Travel
IAB28-5 Bed & Breakfasts
IAB28-6 Budget Travel
IAB28-7 Business Travel
IAB28-8 Camping
IAB28-9 Canada Travel
IAB28-10 Caribbean Travel
IAB28-11 Cruises
IAB28-12 Eastern Europe Travel
IAB28-13 Europe Travel
IAB28-14 France Travel
IAB28-15 Greece Travel
IAB28-16 Honeymoons / Romantic Getaways
IAB28-17 Hotels / Resorts
IAB28-18 Italy Travel
IAB28-19 Japan Travel
IAB28-20 Mexico / Central America Travel
IAB28-21 National Parks
IAB28-22 South America Travel
IAB28-23 Spas
IAB28-24 Theme Parks
IAB28-25 Traveling with Kids
IAB28-26 UK Travel
IAB28-27 Vacation Rentals / Airbnb
IAB28-28 Sustainable / Eco Travel
IAB28-29 Luxury Travel
IAB28-30 Road Trips

### Tier 1: Video Gaming (IAB29)
IAB29-1 Console Games
IAB29-2 Games Reviews
IAB29-3 Mobile Gaming
IAB29-4 Online Role-Playing Games / MMO
IAB29-5 PC Games
IAB29-6 Video Game Accessories
IAB29-7 Cloud Gaming / Game Streaming
IAB29-8 Esports (see IAB24-46)
IAB29-9 Retro / Classic Gaming
IAB29-10 Game Development / Indie Games
""".strip()
