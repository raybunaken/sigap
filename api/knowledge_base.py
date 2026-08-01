"""
SIGAP — Knowledge Base v2
Improvements berdasarkan review:
1. Gap analysis eksplisit di system prompt
2. Mapping skill → kursus konsisten via tag
3. Gaji junior vs mid dibedakan
4. Soft skill per role ditambahkan
5. Format output AI distandarisasi
"""

# ── PEKERJAAN DATABASE ─────────────────────────────────────────────────────
# Data gaji: Michael Page, MSBU Konsultan, NodeFlair Indonesia 2025
PEKERJAAN_DATABASE = {
    "Data Analyst": {
        "kategori": "Data & AI",
        "gaji_junior": "Rp 6.000.000 – 9.000.000",
        "gaji_mid":    "Rp 9.000.000 – 16.000.000",
        "gaji_senior": "Rp 16.000.000 – 28.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["SQL", "Python", "Data Visualization", "Data Cleansing", "Statistical Analysis"],
        "skill_plus":  ["Power BI", "Tableau", "Google Analytics", "BigQuery"],
        "skill_advanced": ["Predictive Modeling", "Big Data Analytics"],
        "soft_skill":  ["Analitis", "Komunikasi", "Problem Solving", "Presentasi"],
        "tools":       ["Excel", "SQL Server", "Tableau", "Power BI"],
        "sertifikasi": ["Google Data Analytics (Coursera — audit gratis)", "Microsoft Power BI Data Analyst (Microsoft Learn)"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Volume data korporasi Indonesia tumbuh pesat — demand visualisasi dan analisis taktis sangat tinggi",
        "skill_tags":  ["sql", "python", "excel", "tableau", "power bi", "data visualization", "statistical analysis"],
    },
    "Data Scientist": {
        "kategori": "Data & AI",
        "gaji_junior": "Rp 8.000.000 – 12.000.000",
        "gaji_mid":    "Rp 12.000.000 – 22.000.000",
        "gaji_senior": "Rp 22.000.000 – 40.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Python", "Machine Learning", "Statistics", "Data Wrangling", "SQL"],
        "skill_plus":  ["Deep Learning", "Natural Language Processing", "Feature Engineering", "Docker"],
        "skill_advanced": ["Generative AI", "MLOps"],
        "soft_skill":  ["Critical Thinking", "Problem Solving", "Communication", "Business Understanding"],
        "tools":       ["Jupyter Notebook", "TensorFlow", "Scikit-Learn", "SQL"],
        "sertifikasi": ["IBM Data Science Professional Certificate (Coursera — audit gratis)", "DeepLearning.AI TensorFlow Developer"],
        "lokasi":      ["Jakarta", "Tangerang", "Bandung", "Remote"],
        "growth":      "Model prediktif untuk fintech dan e-commerce Indonesia memacu demand Data Scientist yang bisa deploy ke production",
        "skill_tags":  ["python", "machine learning", "statistics", "sql", "data wrangling", "deep learning"],
    },
    "Data Engineer": {
        "kategori": "Data & AI",
        "gaji_junior": "Rp 8.000.000 – 13.000.000",
        "gaji_mid":    "Rp 13.000.000 – 24.000.000",
        "gaji_senior": "Rp 24.000.000 – 42.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["SQL", "Python", "ETL Process", "Data Pipeline", "Data Warehousing"],
        "skill_plus":  ["Apache Spark", "BigQuery", "Apache Airflow", "Data Modeling"],
        "skill_advanced": ["Distributed Systems", "Data Lakehouse Architecture"],
        "soft_skill":  ["Logical Thinking", "Problem Solving", "Attention to Detail", "Collaboration"],
        "tools":       ["PostgreSQL", "Apache Airflow", "Google BigQuery", "Git"],
        "sertifikasi": ["Google Professional Data Engineer (Coursera — audit gratis)", "AWS Certified Data Engineer Associate"],
        "lokasi":      ["Jakarta", "Surabaya", "Bandung", "Remote"],
        "growth":      "Korporasi dan startup Indonesia beralih ke arsitektur data modern — fondasi pipeline yang scalable jadi prioritas",
        "skill_tags":  ["sql", "python", "etl", "data pipeline", "cloud computing", "data warehousing"],
    },
    "Machine Learning Engineer": {
        "kategori": "Data & AI",
        "gaji_junior": "Rp 9.000.000 – 14.000.000",
        "gaji_mid":    "Rp 14.000.000 – 26.000.000",
        "gaji_senior": "Rp 26.000.000 – 48.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Python", "Machine Learning", "Deep Learning", "Model Deployment", "Git"],
        "skill_plus":  ["Computer Vision", "Natural Language Processing", "Docker", "MLOps"],
        "skill_advanced": ["LLM Finetuning", "Model Optimization"],
        "soft_skill":  ["Mathematical Logic", "Critical Thinking", "Research Skills", "Problem Solving"],
        "tools":       ["PyTorch", "TensorFlow", "Scikit-Learn", "Docker"],
        "sertifikasi": ["TensorFlow Developer Certificate (Google)", "AWS Certified Machine Learning Specialty"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Adopsi AI generatif di bisnis digital Indonesia mempercepat demand MLE yang bisa deploy model secara efisien",
        "skill_tags":  ["python", "machine learning", "deep learning", "docker", "model deployment", "git"],
    },
    "Backend Developer": {
        "kategori": "Software Engineering",
        "gaji_junior": "Rp 7.000.000 – 11.000.000",
        "gaji_mid":    "Rp 11.000.000 – 20.000.000",
        "gaji_senior": "Rp 20.000.000 – 35.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Node.js", "Python", "SQL", "RESTful API", "Git"],
        "skill_plus":  ["Docker", "Redis", "Database Optimization", "Testing"],
        "skill_advanced": ["Microservices Architecture", "System Design"],
        "soft_skill":  ["Logical Thinking", "Problem Solving", "Collaboration", "Debugging Mindset"],
        "tools":       ["VS Code", "Postman", "PostgreSQL", "GitHub"],
        "sertifikasi": ["Belajar Membuat Back-End Pemula (Dicoding — Gratis)", "AWS Certified Developer Associate"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Hampir semua platform digital butuh backend solid — transisi ke microservices dan API-first terus memperluas demand",
        "skill_tags":  ["node.js", "python", "sql", "git", "restful api", "docker", "backend"],
    },
    "Frontend Developer": {
        "kategori": "Software Engineering",
        "gaji_junior": "Rp 6.500.000 – 10.000.000",
        "gaji_mid":    "Rp 10.000.000 – 18.000.000",
        "gaji_senior": "Rp 18.000.000 – 32.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["HTML", "CSS", "JavaScript", "React.js", "Git"],
        "skill_plus":  ["TypeScript", "Next.js", "Responsive Web Design", "Testing"],
        "skill_advanced": ["Web Performance Optimization", "Design Systems"],
        "soft_skill":  ["Attention to Detail", "Communication", "Empathy for Users", "Creativity"],
        "tools":       ["VS Code", "GitHub", "Figma", "NPM"],
        "sertifikasi": ["Belajar Dasar Pemrograman Web (Dicoding — Gratis)", "Meta Front-End Developer (Coursera — audit gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Persaingan UX tinggi antar web-app mendorong demand Frontend Developer yang bisa buat interface mulus dan interaktif",
        "skill_tags":  ["html", "css", "javascript", "react.js", "git", "frontend", "react"],
    },
    "Full Stack Developer": {
        "kategori": "Software Engineering",
        "gaji_junior": "Rp 8.000.000 – 12.000.000",
        "gaji_mid":    "Rp 12.000.000 – 22.000.000",
        "gaji_senior": "Rp 22.000.000 – 38.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["JavaScript", "Node.js", "React.js", "SQL", "Git"],
        "skill_plus":  ["Docker", "RESTful API", "TypeScript", "Cloud Hosting"],
        "skill_advanced": ["System Design", "CI CD Implementation"],
        "soft_skill":  ["Problem Solving", "Multi-tasking", "Communication", "Adaptability"],
        "tools":       ["VS Code", "GitHub", "Postman", "Docker"],
        "sertifikasi": ["Dicoding Full-Stack Developer Path (Dicoding — Gratis)", "Meta Back-End Developer (Coursera — audit gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Startup menengah-kecil sangat butuh Full Stack Developer karena efisiensi tim IT — satu orang kuasai frontend dan backend",
        "skill_tags":  ["javascript", "node.js", "react.js", "sql", "git", "web development", "react"],
    },
    "Mobile Developer": {
        "kategori": "Software Engineering",
        "gaji_junior": "Rp 7.000.000 – 11.000.000",
        "gaji_mid":    "Rp 11.000.000 – 20.000.000",
        "gaji_senior": "Rp 20.000.000 – 35.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Flutter", "Dart", "RESTful API Integration", "Mobile UI Design", "Git"],
        "skill_plus":  ["Kotlin", "State Management", "Firebase", "Android SDK"],
        "skill_advanced": ["App Store Publishing", "Performance Tuning"],
        "soft_skill":  ["User-centric Mindset", "Problem Solving", "Detail Orientation", "Collaboration"],
        "tools":       ["Android Studio", "VS Code", "Flutter SDK", "Git"],
        "sertifikasi": ["Flutter Developer (Dicoding — Gratis)", "Google Associate Android Developer"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Penetrasi smartphone tinggi di Indonesia menuntut bisnis punya mobile app yang cepat, andal, dan ramah pengguna",
        "skill_tags":  ["flutter", "dart", "git", "mobile development", "restful api", "firebase"],
    },
    "QA Engineer": {
        "kategori": "Software Engineering",
        "gaji_junior": "Rp 5.500.000 – 8.500.000",
        "gaji_mid":    "Rp 8.500.000 – 15.000.000",
        "gaji_senior": "Rp 15.000.000 – 25.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Manual Testing", "Test Case Creation", "Bug Tracking", "API Testing", "SQL"],
        "skill_plus":  ["Selenium", "JavaScript", "Automation Testing", "Load Testing"],
        "skill_advanced": ["CI CD Pipeline Integration", "Performance Testing Automation"],
        "soft_skill":  ["Analytical Mindset", "Attention to Detail", "Clear Communication", "Patience"],
        "tools":       ["Jira", "Postman", "Selenium", "Git"],
        "sertifikasi": ["ISTQB Certified Tester Foundation Level", "freeCodeCamp Quality Assurance (freeCodeCamp — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Standar kualitas software makin tinggi — tim developer adopsi automated testing sejak awal rilis",
        "skill_tags":  ["manual testing", "test case", "bug tracking", "postman", "git", "sql", "automation testing"],
    },
    "Cloud Engineer": {
        "kategori": "IT Infrastructure & Security",
        "gaji_junior": "Rp 8.000.000 – 12.000.000",
        "gaji_mid":    "Rp 12.000.000 – 22.000.000",
        "gaji_senior": "Rp 22.000.000 – 38.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Cloud Computing", "Linux Administration", "Networking Fundamentals", "Docker", "Cloud Security"],
        "skill_plus":  ["Terraform", "Kubernetes", "Python", "Infrastructure as Code"],
        "skill_advanced": ["Multi-cloud Architecture", "FinOps"],
        "soft_skill":  ["Problem Solving", "Continuous Learning", "Teamwork", "Analytical Thinking"],
        "tools":       ["AWS Console", "Linux Terminal", "Docker", "Terraform"],
        "sertifikasi": ["AWS Cloud Practitioner (AWS Skill Builder — Gratis)", "Microsoft Azure Fundamentals (Microsoft Learn — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Tangerang", "Remote"],
        "growth":      "Adopsi cloud masif di sektor finansial dan korporat Indonesia — demand Cloud Engineer meningkat pesat",
        "skill_tags":  ["cloud computing", "linux", "aws", "docker", "networking", "cloud security"],
    },
    "DevOps Engineer": {
        "kategori": "IT Infrastructure & Security",
        "gaji_junior": "Rp 8.500.000 – 13.000.000",
        "gaji_mid":    "Rp 13.000.000 – 25.000.000",
        "gaji_senior": "Rp 25.000.000 – 45.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["CI CD Pipelines", "Linux Administration", "Docker", "Git", "Cloud Computing"],
        "skill_plus":  ["Kubernetes", "Terraform", "Monitoring Tools", "Automation Scripting"],
        "skill_advanced": ["DevSecOps Integration", "Site Reliability Engineering"],
        "soft_skill":  ["Collaboration", "Problem Solving", "System Thinking", "Agility"],
        "tools":       ["Docker", "Jenkins", "Kubernetes", "GitHub Actions"],
        "sertifikasi": ["AWS Certified DevOps Engineer (AWS)", "Belajar Dasar Git (Dicoding — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Siklus rilis produk makin cepat — korporasi teknologi adopsi DevOps untuk satukan dev dan ops secara otomatis",
        "skill_tags":  ["docker", "devops", "cloud computing", "git", "linux", "ci cd", "kubernetes"],
    },
    "Cybersecurity Analyst": {
        "kategori": "IT Infrastructure & Security",
        "gaji_junior": "Rp 7.500.000 – 12.000.000",
        "gaji_mid":    "Rp 12.000.000 – 22.000.000",
        "gaji_senior": "Rp 22.000.000 – 40.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Network Security", "Incident Response", "Vulnerability Assessment", "Linux", "Security Compliance"],
        "skill_plus":  ["Penetration Testing", "SIEM Tools", "Python", "Cryptography"],
        "skill_advanced": ["Security Architecture", "Advanced Forensic Analysis"],
        "soft_skill":  ["Attention to Detail", "Analytical Thinking", "Ethical Mindset", "Communication"],
        "tools":       ["Wireshark", "Nmap", "Splunk", "Kali Linux"],
        "sertifikasi": ["Foundations of Cybersecurity (Coursera — audit gratis)", "CompTIA Security+"],
        "lokasi":      ["Jakarta", "Surabaya", "Tangerang", "Remote"],
        "growth":      "Insiden kebocoran data nasional memicu kesadaran regulasi perlindungan data — tenaga siber makin langka dan mahal",
        "skill_tags":  ["cybersecurity", "linux", "networking", "network security", "wireshark", "vulnerability assessment"],
    },
    "IT Support": {
        "kategori": "IT Infrastructure & Security",
        "gaji_junior": "Rp 4.500.000 – 6.500.000",
        "gaji_mid":    "Rp 6.500.000 – 10.000.000",
        "gaji_senior": "Rp 10.000.000 – 16.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Hardware Troubleshooting", "Operating Systems", "Networking Basics", "Active Directory", "Customer Service"],
        "skill_plus":  ["Linux Basics", "ITIL Framework", "Helpdesk Ticketing", "Basic Scripting"],
        "skill_advanced": ["Network Administration", "IT Infrastructure Management"],
        "soft_skill":  ["Patience", "Communication", "Problem Solving", "Time Management"],
        "tools":       ["Windows Server", "Active Directory", "Jira Service Desk", "TeamViewer"],
        "sertifikasi": ["Google IT Support Professional (Coursera — audit gratis)", "CompTIA A+"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Medan"],
        "growth":      "Setiap instansi dan perusahaan butuh IT Support harian untuk menjaga stabilitas infrastruktur perkantoran",
        "skill_tags":  ["it support", "networking", "troubleshooting", "active directory", "hardware", "operating systems"],
    },
    "UI/UX Designer": {
        "kategori": "Product & Design",
        "gaji_junior": "Rp 6.000.000 – 9.000.000",
        "gaji_mid":    "Rp 9.000.000 – 16.000.000",
        "gaji_senior": "Rp 16.000.000 – 28.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["User Research", "Wireframing", "UI Prototyping", "Figma", "Usability Testing"],
        "skill_plus":  ["Interaction Design", "UX Writing", "Design Systems", "HTML CSS Basics"],
        "skill_advanced": ["Design Leadership", "Conversion Rate Optimization"],
        "soft_skill":  ["Empathy", "Collaboration", "Communication", "Critical Thinking"],
        "tools":       ["Figma", "Adobe XD", "Miro", "Maze"],
        "sertifikasi": ["Google UX Design (Coursera — audit gratis)", "Interaction Design Foundation Certificate"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Bisnis digital Indonesia sadar UX produk berkorelasi langsung dengan retensi user dan kesuksesan transaksi",
        "skill_tags":  ["figma", "user research", "wireframing", "ui prototyping", "usability testing", "ui ux"],
    },
    "Product Manager": {
        "kategori": "Product & Design",
        "gaji_junior": "Rp 9.000.000 – 15.000.000",
        "gaji_mid":    "Rp 15.000.000 – 28.000.000",
        "gaji_senior": "Rp 28.000.000 – 50.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Product Roadmap", "Market Research", "Agile Methodologies", "Data Analysis", "Communication"],
        "skill_plus":  ["SQL", "A/B Testing", "Figma", "Financial Modeling"],
        "skill_advanced": ["Product Strategy", "Growth Hacking"],
        "soft_skill":  ["Leadership", "Stakeholder Management", "Strategic Thinking", "Decision Making"],
        "tools":       ["Jira", "Confluence", "Mixpanel", "Figma"],
        "sertifikasi": ["Google Project Management (Coursera — audit gratis)", "Professional Scrum Product Owner (Scrum.org)"],
        "lokasi":      ["Jakarta", "Tangerang", "Bandung", "Remote"],
        "growth":      "Kebutuhan menjembatani visi bisnis, UX, dan tim developer membuat PM krusial bagi keberlanjutan produk digital",
        "skill_tags":  ["product management", "agile", "market research", "data analysis", "jira", "product roadmap"],
    },
    "Graphic Designer": {
        "kategori": "Product & Design",
        "gaji_junior": "Rp 4.500.000 – 6.500.000",
        "gaji_mid":    "Rp 6.500.000 – 10.000.000",
        "gaji_senior": "Rp 10.000.000 – 16.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Adobe Photoshop", "Adobe Illustrator", "Typography", "Branding Design", "Color Theory"],
        "skill_plus":  ["Canva", "Motion Graphics", "Figma", "Video Editing"],
        "skill_advanced": ["Creative Direction", "Brand Identity Strategy"],
        "soft_skill":  ["Creativity", "Time Management", "Receiving Criticism", "Collaboration"],
        "tools":       ["Adobe Photoshop", "Adobe Illustrator", "Canva", "Figma"],
        "sertifikasi": ["Desain Grafis Komunikasi (Skillhub Kemnaker — Gratis)", "Adobe Certified Professional"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Konten visual masif untuk pemasaran digital membuat Graphic Designer selalu dicari semua sektor industri",
        "skill_tags":  ["graphic design", "canva", "photoshop", "figma", "branding", "adobe illustrator", "typography"],
    },
    "Business Analyst": {
        "kategori": "Business & Management",
        "gaji_junior": "Rp 7.000.000 – 10.000.000",
        "gaji_mid":    "Rp 10.000.000 – 18.000.000",
        "gaji_senior": "Rp 18.000.000 – 30.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Requirements Gathering", "Business Process Modeling", "Data Analysis", "Agile Methodologies", "Excel"],
        "skill_plus":  ["SQL", "Tableau", "Financial Modeling", "Change Management"],
        "skill_advanced": ["Enterprise Architecture", "Strategic Business Planning"],
        "soft_skill":  ["Analytical Thinking", "Stakeholder Management", "Problem Solving", "Communication"],
        "tools":       ["Microsoft Excel", "Miro", "Jira", "Visio"],
        "sertifikasi": ["Business Analysis Foundations (Coursera — audit gratis)", "Agile with Atlassian Jira (Coursera — audit gratis)"],
        "lokasi":      ["Jakarta", "Surabaya", "Tangerang", "Remote"],
        "growth":      "Transformasi digital instansi lama dorong re-engineering proses bisnis tradisional agar lebih lincah dan hemat biaya",
        "skill_tags":  ["business analysis", "excel", "agile", "sql", "requirements gathering", "data analysis"],
    },
    "System Analyst": {
        "kategori": "Business & Management",
        "gaji_junior": "Rp 6.500.000 – 9.500.000",
        "gaji_mid":    "Rp 9.500.000 – 17.000.000",
        "gaji_senior": "Rp 17.000.000 – 28.000.000",
        "demand": "tinggi",
        "skill_wajib": ["UML Modeling", "System Architecture", "Requirements Specification", "SQL", "API Design"],
        "skill_plus":  ["Figma", "Cloud Basics", "Postman", "Enterprise Integration"],
        "skill_advanced": ["Microservices System Design", "IT Governance"],
        "soft_skill":  ["Analytical Thinking", "Communication", "Bridge Builder", "Problem Solving"],
        "tools":       ["Draw.io", "Postman", "Enterprise Architect", "SQL Developer"],
        "sertifikasi": ["System Analysis and Design (Coursera — audit gratis)", "CompTIA IT Fundamentals"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Menerjemahkan kebutuhan bisnis ke spesifikasi sistem IT yang presisi adalah jembatan krusial dalam siklus software",
        "skill_tags":  ["system analyst", "uml", "database", "sql", "api design", "system architecture"],
    },
    "Financial Analyst": {
        "kategori": "Business & Management",
        "gaji_junior": "Rp 7.000.000 – 11.000.000",
        "gaji_mid":    "Rp 11.000.000 – 18.000.000",
        "gaji_senior": "Rp 18.000.000 – 32.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Financial Modeling", "Financial Statement Analysis", "Excel", "Budgeting", "Corporate Finance"],
        "skill_plus":  ["SQL", "Power BI", "Valuation Methods", "Market Research"],
        "skill_advanced": ["M&A Valuation", "Treasury Management"],
        "soft_skill":  ["Numerical Accuracy", "Analytical Thinking", "Ethics", "Communication"],
        "tools":       ["Microsoft Excel", "Power BI", "Bloomberg Terminal", "PowerPoint"],
        "sertifikasi": ["Financial Markets (Coursera Yale — audit gratis)", "CFI Financial Modeling Basics (CFI — Gratis)"],
        "lokasi":      ["Jakarta", "Surabaya", "Tangerang", "Remote"],
        "growth":      "Ketidakpastian ekonomi global buat perusahaan Indonesia makin ketat alokasi modal — analis keuangan makin dicari",
        "skill_tags":  ["financial modeling", "excel", "corporate finance", "power bi", "financial analysis", "budgeting"],
    },
    "Digital Marketing": {
        "kategori": "Digital Marketing & Creative",
        "gaji_junior": "Rp 5.000.000 – 8.000.000",
        "gaji_mid":    "Rp 8.000.000 – 14.000.000",
        "gaji_senior": "Rp 14.000.000 – 24.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["SEO", "Social Media Advertising", "Email Marketing", "Content Strategy", "Web Analytics"],
        "skill_plus":  ["Google Ads", "Copywriting", "Graphic Design", "Video Editing"],
        "skill_advanced": ["Marketing Automation", "Growth Hacking Analytics"],
        "soft_skill":  ["Creativity", "Data Literacy", "Communication", "Adaptability"],
        "tools":       ["Google Analytics", "Meta Ads Manager", "HubSpot", "Mailchimp"],
        "sertifikasi": ["HubSpot Digital Marketing (HubSpot Academy — Gratis)", "Google Ads Certification (Google Skillshop — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Pelaku usaha Indonesia pindah penuh ke online — digital marketing jadi jantung pertumbuhan omset bisnis",
        "skill_tags":  ["digital marketing", "seo", "social media", "copywriting", "google analytics", "email marketing"],
    },
    "Social Media Specialist": {
        "kategori": "Digital Marketing & Creative",
        "gaji_junior": "Rp 4.500.000 – 6.500.000",
        "gaji_mid":    "Rp 6.500.000 – 10.000.000",
        "gaji_senior": "Rp 10.000.000 – 16.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Content Creation", "Social Media Management", "Canva", "Copywriting", "Social Media Analytics"],
        "skill_plus":  ["Video Editing", "Meta Ads", "Influencer Marketing", "Community Engagement"],
        "skill_advanced": ["Social CRM Integration", "Brand Crisis Management"],
        "soft_skill":  ["Creativity", "Empathy", "Time Management", "Adaptability"],
        "tools":       ["Meta Business Suite", "TikTok Business Suite", "Canva", "CapCut"],
        "sertifikasi": ["Introduction to Social Media Marketing (Coursera Meta — audit gratis)", "HubSpot Social Media Marketing (HubSpot — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Sosmed Indonesia dinamis sebagai saluran utama interaksi brand-konsumen — specialist yang bisa analisis data sangat dicari",
        "skill_tags":  ["social media", "content creation", "canva", "copywriting", "instagram", "tiktok", "social media analytics"],
    },
    "Content Creator": {
        "kategori": "Digital Marketing & Creative",
        "gaji_junior": "Rp 4.500.000 – 6.500.000",
        "gaji_mid":    "Rp 6.500.000 – 10.000.000",
        "gaji_senior": "Rp 10.000.000 – 16.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Video Editing", "Script Writing", "Visual Storytelling", "Content Planning", "Canva"],
        "skill_plus":  ["Photography", "Social Media SEO", "Graphic Design", "Public Speaking"],
        "skill_advanced": ["Multi-platform Brand Monetization", "Creative Campaign Management"],
        "soft_skill":  ["Creativity", "Confidence", "Consistency", "Time Management"],
        "tools":       ["CapCut", "Premiere Pro", "Canva", "TikTok"],
        "sertifikasi": ["HubSpot Content Marketing (HubSpot Academy — Gratis)", "Mengoperasikan Media Sosial (Skillhub Kemnaker — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Yogyakarta", "Remote"],
        "growth":      "Tren video pendek TikTok dan Reels memicu ledakan kebutuhan kreator konten kreatif dari brand FMCG hingga startup",
        "skill_tags":  ["content creation", "video editing", "canva", "content planning", "script writing", "capcut"],
    },
    "SEO Specialist": {
        "kategori": "Digital Marketing & Creative",
        "gaji_junior": "Rp 5.500.000 – 8.500.000",
        "gaji_mid":    "Rp 8.500.000 – 14.000.000",
        "gaji_senior": "Rp 14.000.000 – 22.000.000",
        "demand": "tinggi",
        "skill_wajib": ["Keyword Research", "On-Page Optimization", "Off-Page Link Building", "Technical SEO", "Google Analytics"],
        "skill_plus":  ["HTML CSS Basics", "Content Marketing", "WordPress", "A/B Testing"],
        "skill_advanced": ["SEO Automation Scripts", "Core Update Recovery"],
        "soft_skill":  ["Analytical Thinking", "Patience", "Continuous Learning", "Communication"],
        "tools":       ["Google Search Console", "Ahrefs", "Google Analytics", "Screaming Frog"],
        "sertifikasi": ["SEO Certification (HubSpot Academy — Gratis)", "SEO Specialist Dasar (Skillhub Kemnaker — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Traffic organik gratis dari search engine tetap strategi jangka panjang utama startup dan media online Indonesia",
        "skill_tags":  ["seo", "keyword research", "google analytics", "on-page optimization", "technical seo", "link building"],
    },
    "Copywriter": {
        "kategori": "Digital Marketing & Creative",
        "gaji_junior": "Rp 4.500.000 – 7.000.000",
        "gaji_mid":    "Rp 7.000.000 – 11.000.000",
        "gaji_senior": "Rp 11.000.000 – 18.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Persuasive Writing", "SEO Writing", "Brand Voice Alignment", "Headline Creation", "Market Research"],
        "skill_plus":  ["Content Marketing", "Social Media Strategy", "UX Writing", "A/B Testing Copy"],
        "skill_advanced": ["Creative Campaign Ideation", "Conversion Rate Copywriting"],
        "soft_skill":  ["Empathy", "Creativity", "Attention to Detail", "Receptive to Feedback"],
        "tools":       ["Google Docs", "Grammarly", "Canva", "Notion"],
        "sertifikasi": ["Copywriting untuk Pemula (Skillhub Kemnaker — Gratis)", "HubSpot Content Marketing (HubSpot Academy — Gratis)"],
        "lokasi":      ["Jakarta", "Bandung", "Surabaya", "Remote"],
        "growth":      "Di era distraksi digital, kemampuan tulis pesan persuasif yang picu konversi pembeli adalah aset emas tim marketing",
        "skill_tags":  ["copywriting", "seo writing", "content marketing", "digital marketing", "persuasive writing"],
    },
    "Admin E-Commerce": {
        "kategori": "Digital Marketing & Creative",
        "gaji_junior": "Rp 4.000.000 – 5.500.000",
        "gaji_mid":    "Rp 5.500.000 – 8.500.000",
        "gaji_senior": "Rp 8.500.000 – 13.000.000",
        "demand": "sangat tinggi",
        "skill_wajib": ["Product Listing Management", "Customer Service", "Order Processing", "Inventory Tracking", "Excel"],
        "skill_plus":  ["Copywriting", "Digital Ads Operations", "Basic Photo Editing", "Sales Negotiation"],
        "skill_advanced": ["E-Commerce Marketing Strategy", "Supply Chain Analytics"],
        "soft_skill":  ["Communication", "Accuracy", "Stress Tolerance", "Time Management"],
        "tools":       ["Shopee Seller Center", "Tokopedia Seller", "Microsoft Excel", "Canva"],
        "sertifikasi": ["Administrasi E-Commerce (Skillhub Kemnaker — Gratis)", "Learn E-Commerce Marketing (HubSpot Academy — Gratis)"],
        "lokasi":      ["Jakarta", "Surabaya", "Bandung", "Tangerang"],
        "growth":      "Ribuan brand lokal baru di ekosistem belanja online Indonesia butuh admin handal untuk kelola operasional toko digital",
        "skill_tags":  ["e-commerce", "shopee", "tokopedia", "customer service", "excel", "product listing", "inventory"],
    },
}

KURSUS_GRATIS = [
    # ── DICODING (platform tech Indonesia, bersertifikat) ──
    {"nama": "Belajar Dasar Pemrograman Web",           "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-pemrograman-web",          "biaya": "GRATIS", "skill_tags": ["HTML", "CSS", "Responsive Web Design", "web development", "frontend"]},
    {"nama": "Belajar Dasar Pemrograman JavaScript",    "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-pemrograman-javascript",    "biaya": "GRATIS", "skill_tags": ["JavaScript", "web development", "programming"]},
    {"nama": "Memulai Pemrograman dengan Python",        "platform": "Dicoding", "url": "dicoding.com/academies/memulai-pemrograman-dengan-python",        "biaya": "GRATIS", "skill_tags": ["Python", "ETL Process", "Data Pipeline", "programming"]},
    {"nama": "Belajar Dasar SQL",                        "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-structured-query-language-sql","biaya": "GRATIS", "skill_tags": ["SQL", "Database", "Data Warehousing", "Data Analysis", "API Design"]},
    {"nama": "Belajar Dasar AI",                         "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-ai",                         "biaya": "GRATIS", "skill_tags": ["Machine Learning", "Deep Learning", "AI", "artificial intelligence"]},
    {"nama": "Belajar Machine Learning untuk Pemula",   "platform": "Dicoding", "url": "dicoding.com/academies/belajar-machine-learning-untuk-pemula",   "biaya": "GRATIS", "skill_tags": ["Machine Learning", "Python", "Deep Learning", "Model Deployment", "Statistics"]},
    {"nama": "Belajar Dasar Git dengan GitHub",          "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-git-dengan-github",          "biaya": "GRATIS", "skill_tags": ["Git", "CI CD Pipelines", "DevOps", "version control"]},
    {"nama": "Belajar Dasar Analisis Data",              "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-analisis-data",              "biaya": "GRATIS", "skill_tags": ["Data Analysis", "Excel", "Python", "Statistical Analysis", "Data Cleansing"]},
    {"nama": "Belajar Dasar Data Science",               "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-data-science",               "biaya": "GRATIS", "skill_tags": ["Data Wrangling", "Python", "Machine Learning", "Statistics", "Data Pipeline"]},
    {"nama": "Belajar Membuat Back-End untuk Pemula",    "platform": "Dicoding", "url": "dicoding.com/academies/belajar-membuat-aplikasi-back-end-untuk-pemula", "biaya": "GRATIS", "skill_tags": ["Node.js", "RESTful API", "Backend", "API Design", "JavaScript"]},
    {"nama": "Belajar Membuat Front-End Web untuk Pemula","platform": "Dicoding", "url": "dicoding.com/academies/belajar-membuat-front-end-web-untuk-pemula", "biaya": "GRATIS", "skill_tags": ["HTML", "CSS", "JavaScript", "Frontend", "React.js"]},
    {"nama": "Belajar Dasar Cloud Computing",            "platform": "Dicoding", "url": "dicoding.com/academies/belajar-dasar-cloud-computing",            "biaya": "GRATIS", "skill_tags": ["Cloud Computing", "AWS", "Cloud Security", "Networking Fundamentals"]},
    {"nama": "Flutter Developer",                        "platform": "Dicoding", "url": "dicoding.com/academies/352",                                       "biaya": "GRATIS", "skill_tags": ["Flutter", "Dart", "Mobile Developer", "Mobile UI Design"]},
    {"nama": "React Developer",                          "platform": "Dicoding", "url": "dicoding.com/academies/403",                                       "biaya": "GRATIS", "skill_tags": ["React.js", "JavaScript", "Frontend"]},
    # ── SKILLHUB KEMNAKER (pemerintah Indonesia, gratis) ──
    {"nama": "Mengoperasikan Aplikasi Media Sosial",    "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": ["Social Media Management", "Content Creation", "Social Media Analytics", "Instagram", "TikTok", "Community Engagement"]},
    {"nama": "Desain Grafis Komunikasi",                 "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": ["Adobe Photoshop", "Adobe Illustrator", "Typography", "Branding Design", "Color Theory", "Canva", "Graphic Design"]},
    {"nama": "Copywriting untuk Pemula",                 "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": ["Copywriting", "Persuasive Writing", "Headline Creation", "Brand Voice Alignment", "SEO Writing"]},
    {"nama": "SEO Specialist Dasar",                     "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": ["SEO", "Keyword Research", "On-Page Optimization", "Google Analytics"]},
    {"nama": "Administrasi E-Commerce",                  "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": ["Product Listing Management", "Order Processing", "Inventory Tracking", "Customer Service", "E-Commerce"]},
    {"nama": "Teknisi Jaringan dan IT Support",          "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": ["Networking Basics", "Hardware Troubleshooting", "Operating Systems", "IT Support", "Active Directory"]},
    # ── COURSERA (audit gratis, dari institusi global) ──
    {"nama": "Google Data Analytics Professional",       "platform": "Coursera",          "url": "coursera.org/professional-certificates/google-data-analytics",      "biaya": "Gratis (Audit)", "skill_tags": ["Data Analysis", "SQL", "Data Visualization", "Tableau", "Statistical Analysis", "Data Cleansing"]},
    {"nama": "Google UX Design Professional",            "platform": "Coursera",          "url": "coursera.org/professional-certificates/google-ux-design",            "biaya": "Gratis (Audit)", "skill_tags": ["User Research", "Wireframing", "UI Prototyping", "Figma", "Usability Testing", "UX Writing"]},
    {"nama": "Google IT Support Professional",           "platform": "Coursera",          "url": "coursera.org/professional-certificates/google-it-support",           "biaya": "Gratis (Audit)", "skill_tags": ["Hardware Troubleshooting", "Operating Systems", "Networking Basics", "Active Directory", "Customer Service"]},
    {"nama": "Google Project Management Professional",   "platform": "Coursera",          "url": "coursera.org/professional-certificates/google-project-management",   "biaya": "Gratis (Audit)", "skill_tags": ["Agile Methodologies", "Product Roadmap", "Market Research", "Communication"]},
    {"nama": "Foundations of Cybersecurity (Google)",    "platform": "Coursera",          "url": "coursera.org/learn/foundations-of-cybersecurity",                    "biaya": "Gratis (Audit)", "skill_tags": ["Network Security", "Incident Response", "Vulnerability Assessment", "Security Compliance", "Linux"]},
    {"nama": "AWS Cloud Practitioner Essentials",        "platform": "Coursera",          "url": "coursera.org/learn/aws-cloud-practitioner-essentials",              "biaya": "Gratis (Audit)", "skill_tags": ["Cloud Computing", "AWS", "Cloud Security", "Networking Fundamentals", "Docker"]},
    {"nama": "IBM Data Science Professional",             "platform": "Coursera",          "url": "coursera.org/professional-certificates/ibm-data-science",             "biaya": "Gratis (Audit)", "skill_tags": ["Data Science", "Python", "Machine Learning", "Data Wrangling", "SQL", "Statistics"]},
    {"nama": "Deep Learning Specialization (Andrew Ng)", "platform": "Coursera",          "url": "coursera.org/specializations/deep-learning",                        "biaya": "Gratis (Audit)", "skill_tags": ["Deep Learning", "TensorFlow", "Python", "Machine Learning", "Model Deployment"]},
    {"nama": "Meta Front-End Developer Professional",    "platform": "Coursera",          "url": "coursera.org/professional-certificates/meta-front-end-developer",    "biaya": "Gratis (Audit)", "skill_tags": ["React.js", "JavaScript", "HTML", "CSS", "Frontend"]},
    {"nama": "Meta Social Media Marketing",              "platform": "Coursera",          "url": "coursera.org/professional-certificates/meta-social-media-marketing",  "biaya": "Gratis (Audit)", "skill_tags": ["Social Media Management", "Social Media Analytics", "Content Creation", "Meta Ads", "Community Engagement"]},
    {"nama": "Software Testing and QA",                  "platform": "Coursera",          "url": "coursera.org/learn/software-testing-and-qa",                        "biaya": "Gratis (Audit)", "skill_tags": ["Manual Testing", "Test Case Creation", "Bug Tracking", "API Testing", "Automation Testing"]},
    {"nama": "Business Analysis Foundations",            "platform": "Coursera",          "url": "coursera.org/learn/business-analysis-foundations",                  "biaya": "Gratis (Audit)", "skill_tags": ["Requirements Gathering", "Business Process Modeling", "Agile Methodologies", "Data Analysis"]},
    {"nama": "System Analysis and Design",               "platform": "Coursera",          "url": "coursera.org/learn/system-analysis-design",                         "biaya": "Gratis (Audit)", "skill_tags": ["UML Modeling", "System Architecture", "Requirements Specification", "API Design"]},
    {"nama": "Financial Markets (Yale)",                 "platform": "Coursera",          "url": "coursera.org/learn/financial-markets-global",                       "biaya": "Gratis (Audit)", "skill_tags": ["Corporate Finance", "Financial Statement Analysis", "Budgeting", "Valuation Methods"]},
    {"nama": "Agile with Atlassian Jira",                "platform": "Coursera",          "url": "coursera.org/learn/agile-atlassian-jira",                           "biaya": "Gratis (Audit)", "skill_tags": ["Agile Methodologies", "Requirements Gathering", "Business Process Modeling"]},
    {"nama": "Introduction to Product Management",       "platform": "Coursera",          "url": "coursera.org/learn/introduction-to-product-management-by-cognizant", "biaya": "Gratis (Audit)", "skill_tags": ["Product Roadmap", "Market Research", "Product Lifecycle Management"]},
    # ── HUBSPOT ACADEMY (gratis + sertifikat) ──
    {"nama": "HubSpot Digital Marketing",                "platform": "HubSpot Academy",  "url": "academy.hubspot.com/courses/digital-marketing",         "biaya": "GRATIS + Sertifikat", "skill_tags": ["SEO", "Email Marketing", "Web Analytics", "Content Strategy", "Social Media Advertising"]},
    {"nama": "HubSpot Content Marketing",                "platform": "HubSpot Academy",  "url": "academy.hubspot.com/courses/content-marketing",         "biaya": "GRATIS + Sertifikat", "skill_tags": ["Content Strategy", "Script Writing", "Visual Storytelling", "Content Planning", "Persuasive Writing"]},
    {"nama": "HubSpot SEO Certification",                "platform": "HubSpot Academy",  "url": "academy.hubspot.com/courses/seo",                        "biaya": "GRATIS + Sertifikat", "skill_tags": ["SEO", "Keyword Research", "On-Page Optimization", "Off-Page Link Building", "Technical SEO", "SEO Writing"]},
    {"nama": "HubSpot Social Media Marketing",           "platform": "HubSpot Academy",  "url": "academy.hubspot.com/courses/social-media",               "biaya": "GRATIS + Sertifikat", "skill_tags": ["Social Media Management", "Content Creation", "Social Media Analytics", "Community Engagement"]},
    {"nama": "HubSpot Inbound Marketing",                "platform": "HubSpot Academy",  "url": "academy.hubspot.com/courses/inbound-marketing",         "biaya": "GRATIS + Sertifikat", "skill_tags": ["Content Strategy", "Email Marketing", "Web Analytics", "Copywriting"]},
    # ── PLATFORM LAIN ──
    {"nama": "freeCodeCamp Responsive Web Design",       "platform": "freeCodeCamp",      "url": "freecodecamp.org/learn/responsive-web-design",          "biaya": "GRATIS", "skill_tags": ["HTML", "CSS", "Responsive Web Design", "Frontend"]},
    {"nama": "freeCodeCamp Quality Assurance",           "platform": "freeCodeCamp",      "url": "freecodecamp.org/learn/quality-assurance",              "biaya": "GRATIS", "skill_tags": ["Manual Testing", "Test Case Creation", "Bug Tracking", "Automation Testing"]},
    {"nama": "Microsoft Power BI",                       "platform": "Microsoft Learn",   "url": "learn.microsoft.com/power-bi",                          "biaya": "GRATIS", "skill_tags": ["Power BI", "Data Visualization", "Financial Modeling", "Business Analysis"]},
    {"nama": "Microsoft Azure Fundamentals",             "platform": "Microsoft Learn",   "url": "learn.microsoft.com/azure",                             "biaya": "GRATIS", "skill_tags": ["Cloud Computing", "Cloud Security", "Networking Fundamentals"]},
    {"nama": "TypeScript",                              "platform": "Microsoft Learn",   "url": "learn.microsoft.com/typescript",                        "biaya": "GRATIS", "skill_tags": ["TypeScript", "JavaScript", "Frontend"]},
    {"nama": "AWS Cloud Practitioner",                   "platform": "AWS Skill Builder", "url": "skillbuilder.aws",                                       "biaya": "GRATIS", "skill_tags": ["Cloud Computing", "AWS", "Cloud Security", "CI CD Pipelines"]},
    {"nama": "Canva Design School",                      "platform": "Canva",             "url": "designschool.canva.com",                                 "biaya": "GRATIS", "skill_tags": ["Canva", "Visual Storytelling", "Content Creation", "Branding Design"]},
    {"nama": "CFI Financial Modeling Basics",            "platform": "CFI",               "url": "corporatefinanceinstitute.com",                          "biaya": "GRATIS", "skill_tags": ["Financial Modeling", "Excel", "Corporate Finance", "Budgeting", "Valuation Methods"]},
    {"nama": "Google Ads Certification",                 "platform": "Google Skillshop",  "url": "skillshop.withgoogle.com",                              "biaya": "GRATIS", "skill_tags": ["Social Media Advertising", "Digital Marketing", "Web Analytics"]},
    {"nama": "Cisco Networking Basics",                  "platform": "Cisco NetAcad",     "url": "netacad.com/courses/networking",                         "biaya": "GRATIS", "skill_tags": ["Networking Basics", "Networking Fundamentals", "IT Support", "Active Directory"]},
]

# ── ROADMAP ────────────────────────────────────────────────────────────────
ROADMAP = {
    "Data Analyst": [
        {"fase": "Bulan 1-2", "nama": "Fondasi",     "skill": ["Excel", "SQL Dasar", "Statistik Dasar"], "kursus": "SQL untuk Pemula (Dicoding — Gratis)",          "milestone": "Bisa query database dan buat laporan sederhana"},
        {"fase": "Bulan 3-4", "nama": "Core Skills", "skill": ["Python Pandas", "Visualisasi Data"],     "kursus": "Google Data Analytics (Coursera — audit gratis atau Skillhub Kemnaker)",     "milestone": "Bisa analisis dataset dan buat dashboard interaktif"},
        {"fase": "Bulan 5-6", "nama": "Portofolio",  "skill": ["Tableau/Power BI", "Kaggle Project"],    "kursus": "Microsoft Power BI (Microsoft Learn — Gratis)", "milestone": "3 project portofolio di GitHub — ini yang paling penting!"},
    ],
    "Data Scientist": [
        {"fase": "Bulan 1-3", "nama": "Fondasi",       "skill": ["Python", "Statistik & Math", "SQL"],    "kursus": "Belajar Python (Dicoding — Gratis)",                 "milestone": "Paham konsep ML dan bisa implementasi model dasar"},
        {"fase": "Bulan 4-6", "nama": "Machine Learning","skill": ["Scikit-learn", "Feature Engineering"], "kursus": "Machine Learning Terapan (Dicoding — Gratis)",       "milestone": "Selesaikan 2-3 Kaggle competition"},
        {"fase": "Bulan 7-9", "nama": "Spesialisasi",  "skill": ["Deep Learning", "NLP atau CV"],         "kursus": "Deep Learning Specialization (Coursera — audit gratis)","milestone": "Project end-to-end yang di-deploy online"},
    ],
    "Backend Developer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi",    "skill": ["Python/Node.js", "Git", "SQL"],               "kursus": "Belajar Python (Dicoding — Gratis)",         "milestone": "Bisa buat REST API sederhana"},
        {"fase": "Bulan 3-4", "nama": "Framework",  "skill": ["FastAPI/Express", "PostgreSQL", "JWT Auth"],  "kursus": "Backend Developer (Dicoding — Gratis)",     "milestone": "CRUD API lengkap dengan autentikasi"},
        {"fase": "Bulan 5-6", "nama": "Production", "skill": ["Docker", "Cloud Deployment", "Testing"],      "kursus": "AWS Cloud Practitioner (AWS Skill Builder — Gratis)", "milestone": "Deploy aplikasi ke production"},
    ],
    "Frontend Developer": [
        {"fase": "Bulan 1-2", "nama": "Web Dasar", "skill": ["HTML5", "CSS3", "JavaScript ES6+"],     "kursus": "Frontend Developer (Dicoding — Gratis)", "milestone": "Rebuild halaman website dari nol"},
        {"fase": "Bulan 3-4", "nama": "React",     "skill": ["React", "State Management", "API"],    "kursus": "React Developer (Dicoding — Gratis)",    "milestone": "Buat Single Page App yang connect ke API"},
        {"fase": "Bulan 5-6", "nama": "Modern Stack","skill": ["TypeScript", "Next.js", "Testing"],  "kursus": "TypeScript (Microsoft Learn — Gratis)",  "milestone": "3 project di GitHub, deploy ke Vercel"},
    ],
    "UI/UX Designer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi Design", "skill": ["Figma", "Design Principles", "Typography"],   "kursus": "Google UX Design (Coursera — audit gratis)", "milestone": "Bisa buat wireframe dan mockup di Figma"},
        {"fase": "Bulan 3-4", "nama": "UX Process",     "skill": ["User Research", "Usability Testing"],         "kursus": "Interaction Design Foundation (IDF)",  "milestone": "1 full UX case study dari research ke prototype"},
        {"fase": "Bulan 5-6", "nama": "Portofolio",     "skill": ["Case Studies", "Portfolio Website"],           "kursus": "Behance + Dribbble Community",         "milestone": "3 case study di Behance — kualitas > kuantitas"},
    ],
    "Mobile Developer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi",    "skill": ["Dart Dasar", "Flutter Widgets", "Git"],    "kursus": "Flutter Developer (Dicoding — Gratis)", "milestone": "Bisa buat UI sederhana dengan Flutter"},
        {"fase": "Bulan 3-4", "nama": "Core Flutter","skill": ["State Management", "API Integration"],   "kursus": "Flutter Advanced (YouTube/dokumentasi)", "milestone": "App yang connect ke REST API"},
        {"fase": "Bulan 5-6", "nama": "Production", "skill": ["Firebase", "App Store Submission"],        "kursus": "Firebase (dokumentasi resmi — Gratis)",  "milestone": "Publish 1 app ke Play Store"},
    ],
}

STATISTIK = {
    # BPS Sakernas Agustus 2025 (BRS No.103/11/Th.XXVIII, 5 November 2025)
    "rata_upah_nasional":      "Rp 3,33 juta (BPS Agustus 2025)",
    "upah_s1_s2_s3":           "Rp 4,80 juta rata-rata (BPS Agustus 2025)",
    "upah_diploma":            "Rp 4,50 juta rata-rata (BPS Agustus 2025)",
    "upah_sma":                "Rp 3,15 juta rata-rata (BPS Agustus 2025)",
    "upah_smk":                "Rp 3,26 juta rata-rata (BPS Agustus 2025)",
    "upah_sektor_tertinggi":   "Informasi & Komunikasi Rp 5,28 juta (BPS Agustus 2025)",
    # BPS Sakernas Agustus 2024 — ketenagakerjaan
    "pengangguran_terbuka":    "7,47 juta (BPS Agustus 2024)",
    "tpt_agustus_2024":        "4,91% Tingkat Pengangguran Terbuka (BPS Agustus 2024)",
    "rata_lama_cari_kerja":    "6-12 bulan untuk fresh grad",
    "sumber_gaji": "BPS Sakernas Agustus 2025, BRS No.103/11/Th.XXVIII, 5 November 2025 — https://www.bps.go.id",
    "sumber_naker": "BPS Sakernas Agustus 2024, BRS No.64/11/Th.XXVII, 5 November 2024 — https://www.bps.go.id",
}

# ── UNIFIED SKILL SYNONYMS ─────────────────────────────────────────────
# Satu sumber kebenaran untuk semua sinonim skill.
# Key = canonical form (lowercase), Values = list of equivalent terms (lowercase)
SKILL_SYNONYMS = {
    # English skill terms dari Deep Research → match ke bahasa Indonesia dan variasi lain
    "data visualization":   ["visualisasi data", "tableau", "power bi", "looker", "matplotlib", "data viz", "dashboard", "data storytelling"],
    "statistical analysis": ["statistik", "statistics", "spss", "probability", "anova", "statistical"],
    "data analysis":        ["analisis data", "data analytics", "data analyst", "data cleansing", "data wrangling", "data exploration"],
    "machine learning":     ["ml", "ai", "artificial intelligence", "deep learning", "nlp", "scikit", "scikit-learn", "model deployment"],
    "sql":                  ["sql basic", "sql dasar", "database", "mysql", "postgresql", "mongodb", "basis data", "data warehousing"],
    "python":               ["python dasar", "python programming", "memulai pemrograman python"],
    "restful api":          ["rest api", "api design", "apis integration", "api integration", "restful api integration"],
    "ci cd pipelines":      ["ci/cd", "cicd", "continuous integration", "github actions", "jenkins", "devops pipeline"],
    "cloud computing":      ["aws", "gcp", "azure", "cloud engineer", "cloud security", "virtualization"],
    "docker":               ["containerization", "docker compose", "container"],
    "git":                  ["github", "gitlab", "version control", "source control"],
    "react.js":             ["react", "reactjs", "react js"],
    "node.js":              ["node js", "nodejs", "express"],
    "javascript":           ["js", "es6", "vanilla js"],
    "excel":                ["microsoft excel", "ms excel", "spreadsheet", "excel advanced", "excel macros"],
    "microsoft office":     ["excel", "word", "powerpoint", "ms office", "office"],
    "google analytics":     ["ga4", "google analytics 4", "web analytics"],
    "content creation":     ["content planning", "content creator", "konten kreator", "menulis konten", "script writing"],
    "social media":         ["instagram", "tiktok", "sosmed", "media sosial", "social media planning", "social media management"],
    "canva":                ["canva pro", "canva design"],
    "video editing":        ["capcut", "premiere pro", "adobe premiere", "after effects"],
    "figma":                ["figma design", "adobe xd", "ui prototyping", "wireframing"],
    "user research":        ["ux research", "usability testing", "user testing"],
    "copywriting":          ["persuasive writing", "seo writing", "headline creation", "brand voice alignment"],
    "agile methodologies":  ["agile", "scrum", "kanban", "agile/scrum", "sprint"],
    "communication":        ["komunikasi", "public speaking", "presentasi", "komunikasi bisnis"],
    "customer service":     ["customer handling", "pelayanan pelanggan", "cs", "customer support"],
    "network security":     ["keamanan jaringan", "cybersecurity", "information security", "networking"],
    "hardware troubleshooting": ["hardware", "troubleshooting", "komputer"],
    "operating systems":    ["os administration", "windows administration", "linux administration", "linux"],
    "financial modeling":   ["financial model", "valuation methods", "dcf", "valuasi bisnis"],
    "requirements gathering": ["requirement gathering", "brd", "business requirements"],
    "uml modeling":         ["uml", "use case diagram", "flowchart", "bpmn"],
    "product roadmap":      ["roadmap produk", "product thinking", "product lifecycle management"],
    "market research":      ["riset pasar", "competitor analysis", "market analysis"],
    "branding design":      ["brand identity", "logo design", "branding"],
    "seo":                  ["search engine optimization", "search engine", "seo specialist", "on-page seo", "technical seo", "keyword research"],
    "adobe photoshop":      ["photoshop", "ps", "adobe ps"],
    "adobe illustrator":    ["illustrator", "ai", "adobe ai"],
    "etl process":          ["etl", "extract transform load", "data pipeline", "pipeline"],
    "vulnerability assessment": ["vulnerability", "pentest", "penetration testing"],
    "bug tracking":         ["bug report", "defect tracking", "jira", "test case"],
    "manual testing":       ["software testing", "qa testing", "test case creation"],
}

def normalize_skill(skill: str) -> str:
    """Lowercase dan strip whitespace."""
    return skill.strip().lower()

def skills_match(user_skill: str, target_skill: str) -> bool:
    """
    Cek apakah user_skill memenuhi target_skill.
    Menggunakan exact match, substring match, dan synonym matching.
    """
    u = normalize_skill(user_skill)
    t = normalize_skill(target_skill)

    # 1. Exact match
    if u == t:
        return True

    # 2. Substring match (bidirectional)
    if u in t or t in u:
        return True

    # 3. Synonym match — cek apakah keduanya ada di grup sinonim yang sama
    for canon, synonyms in SKILL_SYNONYMS.items():
        all_terms = [canon] + synonyms
        u_in = any(u == term or u in term or term in u for term in all_terms)
        t_in = any(t == term or t in term or term in t for term in all_terms)
        if u_in and t_in:
            return True

    return False

def get_kursus_for_skill(skill: str) -> list:
    """
    Cari kursus yang paling relevan untuk satu skill.
    Pakai skill_tags + synonym matching.
    """
    skill_lower = normalize_skill(skill)
    matches = []
    for k in KURSUS_GRATIS:
        tags_lower = [normalize_skill(t) for t in k.get("skill_tags", [])]
        if any(skills_match(skill_lower, tag) for tag in tags_lower):
            matches.append(k)
    return matches[:2]

def get_gaji_by_experience(job_data: dict, pengalaman: str) -> str:
    """
    Return gaji sesuai level pengalaman.
    Support dua format: estimasi_gaji_freshgrad (baru) dan gaji_junior (lama).
    """
    
    if "estimasi_gaji_freshgrad" in job_data:
        return job_data["estimasi_gaji_freshgrad"]
    
    exp_lower = pengalaman.lower()
    if any(x in exp_lower for x in ["fresh", "belum", "magang", "< 1", "1-2"]):
        return job_data.get("gaji_junior", job_data.get("rata_gaji", "-"))
    elif any(x in exp_lower for x in ["2-5", "3", "4", "5"]):
        return job_data.get("gaji_mid", job_data.get("rata_gaji", "-"))
    elif any(x in exp_lower for x in ["> 5", "senior"]):
        return job_data.get("gaji_senior", job_data.get("rata_gaji", "-"))
    return job_data.get("gaji_junior", job_data.get("rata_gaji", "-"))

# -- SYSTEM PROMPT--
def get_system_prompt(profil: dict = None) -> str:
    profil_str = ""
    kursus_str = ""

    if profil:
        skill_list  = profil.get("skill", [])
        target      = profil.get("target_job", "")
        skill_kurang = profil.get("skill_kurang", [])
        readiness   = profil.get("readiness", 0)

        job_target = profil.get('job_target') or profil.get('target_job') or target
        profil_str = f"""
=== PROFIL USER ===
- Pendidikan    : {profil.get('pendidikan', '-')}
- Skill dimiliki: {', '.join(skill_list) if skill_list else 'belum diisi'}
- Target karir  : {job_target}
- Pengalaman    : {profil.get('pengalaman', 'Fresh grad')}
- Lokasi        : {profil.get('lokasi', '-')}
- Readiness     : {readiness}% {"(Siap Apply!)" if readiness >= 70 else "(Hampir Siap)" if readiness >= 45 else "(Perlu Persiapan)"}

=== HASIL ANALISIS GAP (KONTEKS CHAT) ===
Skill yang SUDAH dimiliki user: {', '.join(skill_list) if skill_list else 'belum ada'}
Skill yang MASIH KURANG (ini yang harus jadi fokus chat): {', '.join(skill_kurang) if skill_kurang else 'tidak ada — sudah siap!'}

INGAT: Saat menjawab pertanyaan apapun, selalu merujuk ke konteks di atas.
Jangan sebut skill lain di luar yang kurang kecuali user minta lebih luas.
"""
        
        kursus_relevan = []
        for sk in skill_kurang[:3]:
            matches = get_kursus_for_skill(sk)
            kursus_relevan.extend(matches)

        if kursus_relevan:
            kursus_str = "\n=== KURSUS GRATIS RELEVAN ===\n"
            seen = set()
            for k in kursus_relevan:
                if k['nama'] not in seen:
                    kursus_str += f"- {k['nama']} ({k['platform']}) — {k['biaya']}\n"
                    seen.add(k['nama'])

    return f"""Kamu adalah SIGAP (Sistem Identifikasi GAP Skill), AI advisor karir untuk mahasiswa dan fresh graduate Indonesia.
{profil_str}{kursus_str}
=== CARA ANALISIS GAP ===
1. Bandingkan skill user dengan skill_wajib pekerjaan target
2. Skill yang ADA di skill_wajib tapi TIDAK dimiliki user = GAP UTAMA → prioritaskan ini
3. Skill yang ADA di skill_plus tapi tidak dimiliki = gap sekunder
4. Kalau readiness < 45% → fokus ke fondasi dulu, jangan langsung advanced
5. Selalu rekomendasikan kursus GRATIS dulu sebelum yang berbayar

=== KONTEKS CHAT (WAJIB DIIKUTI) ===
Jika user sudah melakukan analisis gap sebelumnya, kamu WAJIB merujuk pada:
- [Skill kurang] di atas sebagai referensi utama
- JANGAN sebutkan skill lain yang tidak ada di daftar [Skill kurang] kecuali diminta
- Jika user tanya "kenapa butuh skill itu?" atau "apa itu?", jelaskan skill dari [Skill kurang]
- Jika user tanya "langkah selanjutnya?", buat roadmap berdasarkan [Skill kurang]
- JANGAN halusinasi skill baru yang tidak relevan dengan profil user

=== FORMAT JAWABAN ===
Untuk analisis karir: mulai dengan penilaian jujur skill yang sudah dimiliki,
lalu sebutkan 2-3 skill spesifik yang paling perlu dipelajari (pakai nama asli toolsnya),
rekomendasikan 1-2 kursus gratis yang konkret, dan estimasi waktu realistis.

JANGAN pakai header bold seperti "**Gap Utama:**" — tulis mengalir seperti ngobrol.
Untuk pertanyaan casual/general → jawab natural, singkat, langsung.

=== PENGETAHUAN (SUMBER VALID) ===
Data Gaji — BPS Sakernas Agustus 2025 (sumber resmi, verifiable):
- Rata-rata upah nasional: Rp 3,33 juta/bulan
- Lulusan S1/S2/S3: rata-rata Rp 4,80 juta/bulan
- Lulusan Diploma: rata-rata Rp 4,50 juta/bulan
- Sektor tertinggi: Informasi & Komunikasi Rp 5,28 juta
- Artinya: fresh grad S1 IT bisa expect Rp 4-7 juta, bukan langsung Rp 10 juta+

Data Ketenagakerjaan — BPS Sakernas Agustus 2024:
- TPT (Tingkat Pengangguran Terbuka): 4,91% = sekitar 7,47 juta orang
- Sumber: https://www.bps.go.id

Fakta karir Indonesia:
- Dicoding adalah platform kursus tech Indonesia terbaik — GRATIS dan bersertifikat
- Skillhub Kemnaker (skillhub.kemnaker.go.id) — e-training resmi gratis dari Kemnaker
- Coursera bisa diaudit gratis tanpa sertifikat
- Soft skill (komunikasi, problem solving, teamwork) sama pentingnya dengan hard skill
- Portofolio GitHub > sertifikat untuk fresh grad tech
- Rata-rata waktu dapat kerja pertama: 3-6 bulan dengan persiapan matang

=== GAYA BAHASA ===
- Ngobrol kayak temen senior yang peduli, bukan HR formal
- Pakai "kamu" bukan "Anda"
- Sebut tools dengan nama aslinya: "Hootsuite", "Buffer", "Canva", "Meta Business Suite" — BUKAN "alat bantu media sosial"
- Kalau ada istilah teknis, sebut langsung jangan diterjemahin aneh-aneh
- Boleh pakai analogi yang relatable buat fresh grad
- Jujur kalau memang butuh waktu lama — jangan terlalu hype
- Max 3 paragraf, padat dan to the point
- JANGAN gunakan format bold/italic berlebihan di jawaban casual
- Hindari kalimat klise seperti: jangan khawatir, semangat terus, perjalanan seribu mil"""

# ── ROADMAP TAMBAHAN  ───────────────────────────
_ROADMAP_EXTRA = {
    "Full Stack Developer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi Web", "skill": ["HTML", "CSS", "JavaScript ES6+", "Git"], "kursus": "Frontend Developer (Dicoding — Gratis)", "milestone": "Buat halaman web responsif dari nol"},
        {"fase": "Bulan 3-4", "nama": "Backend + Database", "skill": ["Node.js/Python", "REST API", "SQL", "PostgreSQL"], "kursus": "Backend Developer (Dicoding — Gratis)", "milestone": "CRUD API lengkap yang terkoneksi ke frontend"},
        {"fase": "Bulan 5-6", "nama": "Full Stack Project", "skill": ["React", "Docker", "Deploy ke Cloud"], "kursus": "AWS Cloud Practitioner (AWS Skill Builder — Gratis)", "milestone": "1 aplikasi full stack live di internet"},
    ],
    "Data Engineer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Python", "SQL Advanced", "Linux Dasar"], "kursus": "Belajar Python (Dicoding — Gratis)", "milestone": "Bisa buat ETL pipeline sederhana"},
        {"fase": "Bulan 3-4", "nama": "Data Pipeline", "skill": ["Apache Spark", "Airflow", "Cloud Storage"], "kursus": "GCP Professional Data Engineer (Coursera — Audit Gratis)", "milestone": "Pipeline otomatis yang jalan terjadwal"},
        {"fase": "Bulan 5-6", "nama": "Production", "skill": ["dbt", "BigQuery/Redshift", "Data Warehouse"], "kursus": "dbt Fundamentals (dbt Learn — Gratis)", "milestone": "Data warehouse yang siap dipakai tim analyst"},
    ],
    "Machine Learning Engineer": [
        {"fase": "Bulan 1-3", "nama": "Fondasi ML", "skill": ["Python", "Scikit-learn", "SQL", "Git"], "kursus": "Machine Learning Terapan (Dicoding — Gratis)", "milestone": "Deploy model ML sederhana ke API"},
        {"fase": "Bulan 4-6", "nama": "Deep Learning", "skill": ["TensorFlow/PyTorch", "Feature Engineering", "MLflow"], "kursus": "Deep Learning Specialization (Coursera — Audit Gratis)", "milestone": "Model DL yang tertrack dengan MLflow"},
        {"fase": "Bulan 7-9", "nama": "MLOps", "skill": ["Docker", "FastAPI", "CI/CD untuk ML", "Cloud Deploy"], "kursus": "GCP ML Engineer (Coursera/Skillhub Kemnaker)", "milestone": "Model production yang auto-retrain"},
    ],
    "Cloud Engineer": [
        {"fase": "Bulan 1-2", "nama": "Cloud Dasar", "skill": ["Linux", "Networking Dasar", "AWS/GCP Dasar"], "kursus": "AWS Cloud Practitioner (AWS Skill Builder — Gratis)", "milestone": "Deploy aplikasi sederhana ke cloud"},
        {"fase": "Bulan 3-4", "nama": "Infrastructure", "skill": ["Docker", "Terraform", "IAM & Security"], "kursus": "HashiCorp Terraform Associate (Terraform Learn — Gratis)", "milestone": "Infra as Code yang reproducible"},
        {"fase": "Bulan 5-6", "nama": "Advanced", "skill": ["Kubernetes", "Monitoring", "Cost Optimization"], "kursus": "CKA Preparation (killer.sh)", "milestone": "Certified & portofolio infra di GitHub"},
    ],
    "DevOps Engineer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Linux", "Git", "Bash Scripting", "Docker"], "kursus": "Linux & Bash (freeCodeCamp — Gratis)", "milestone": "Bisa automate task server dengan script"},
        {"fase": "Bulan 3-4", "nama": "CI/CD", "skill": ["GitHub Actions", "Jenkins", "Docker Compose"], "kursus": "GitHub Actions (dokumentasi resmi — Gratis)", "milestone": "Pipeline CI/CD yang jalan otomatis"},
        {"fase": "Bulan 5-6", "nama": "Production", "skill": ["Kubernetes", "Monitoring (Prometheus/Grafana)", "Cloud"], "kursus": "AWS SysOps Administrator (Skillhub Kemnaker)", "milestone": "Cluster K8s yang termanage dengan baik"},
    ],
    "Cybersecurity Analyst": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Linux", "Networking", "Python Scripting"], "kursus": "TryHackMe Free Path (tryhackme.com — Gratis)", "milestone": "Bisa analisis traffic jaringan dasar"},
        {"fase": "Bulan 3-4", "nama": "Security Tools", "skill": ["Wireshark", "Nmap", "Kali Linux", "OWASP Top 10"], "kursus": "CompTIA Security+ Prep (Professor Messer — Gratis)", "milestone": "Bisa identifikasi vulnerability dasar"},
        {"fase": "Bulan 5-6", "nama": "Sertifikasi", "skill": ["Penetration Testing", "Incident Response", "SIEM"], "kursus": "CompTIA Security+ (exam)", "milestone": "Certified + 1 CTF writeup di blog"},
    ],
    "QA Engineer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi Testing", "skill": ["Manual Testing", "Test Case Writing", "Bug Reporting", "Jira"], "kursus": "ISTQB Foundation (buku resmi + komunitas)", "milestone": "Bisa buat test plan dan test case lengkap"},
        {"fase": "Bulan 3-4", "nama": "Automation", "skill": ["Selenium/Cypress", "Python/JavaScript", "API Testing (Postman)"], "kursus": "Selenium WebDriver (Udemy Free Coupon)", "milestone": "Test suite otomatis yang jalan di CI/CD"},
        {"fase": "Bulan 5-6", "nama": "Advanced", "skill": ["Performance Testing (JMeter)", "BDD", "Test Strategy"], "kursus": "ISTQB Foundation Exam", "milestone": "ISTQB certified + portofolio automation"},
    ],
    "Business Analyst": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Excel Advanced", "SQL Dasar", "Requirement Gathering"], "kursus": "Google Data Analytics (Coursera — Audit Gratis)", "milestone": "Bisa buat BRD (Business Requirements Document)"},
        {"fase": "Bulan 3-4", "nama": "Data & Process", "skill": ["Power BI/Tableau", "BPMN", "User Story"], "kursus": "Microsoft Power BI (Microsoft Learn — Gratis)", "milestone": "Dashboard bisnis yang bisa dipresentasikan ke stakeholder"},
        {"fase": "Bulan 5-6", "nama": "Portofolio", "skill": ["Agile/Scrum", "Market Research", "Presentasi Data"], "kursus": "Professional Scrum Master (Scrum.org — trial gratis)", "milestone": "1 studi kasus analisis bisnis lengkap"},
    ],
    "System Analyst": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["SQL", "UML Dasar", "SDLC", "Flowchart"], "kursus": "SQL untuk Pemula (Dicoding — Gratis)", "milestone": "Bisa buat ERD dan use case diagram"},
        {"fase": "Bulan 3-4", "nama": "Analisis Sistem", "skill": ["Figma Dasar", "API Documentation", "Postman"], "kursus": "Google UX Design (Coursera — Audit Gratis)", "milestone": "SRS dokumen yang bisa dipakai developer"},
        {"fase": "Bulan 5-6", "nama": "Implementation", "skill": ["Agile/Scrum", "ITIL Dasar", "Enterprise Architecture"], "kursus": "ITIL Foundation (axelos.com)", "milestone": "1 proyek analisis sistem dari awal sampai dokumentasi"},
    ],
    "Product Manager": [
        {"fase": "Bulan 1-2", "nama": "PM Mindset", "skill": ["Product Thinking", "User Research", "Competitor Analysis"], "kursus": "Google Project Management (Coursera — Audit Gratis)", "milestone": "Bisa buat PRD (Product Requirements Document)"},
        {"fase": "Bulan 3-4", "nama": "Data & Design", "skill": ["SQL Dasar", "Figma Dasar", "A/B Testing", "Analytics"], "kursus": "SQL untuk Pemula (Dicoding — Gratis)", "milestone": "Analisis produk berbasis data yang konkret"},
        {"fase": "Bulan 5-6", "nama": "Roadmap & Launch", "skill": ["Agile/Scrum", "OKR", "Go-to-Market Strategy"], "kursus": "Product School Free Resources (productschool.com)", "milestone": "1 product case study yang bisa dipresentasikan"},
    ],
    "Digital Marketing": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Google Analytics", "SEO Dasar", "Content Planning"], "kursus": "Google Digital Marketing (Skillhub Kemnaker — Gratis)", "milestone": "Bisa buat dan eksekusi content calendar"},
        {"fase": "Bulan 3-4", "nama": "Paid Ads", "skill": ["Google Ads", "Meta Ads", "Email Marketing"], "kursus": "Meta Blueprint (Meta — Gratis)", "milestone": "Campaign iklan pertama dengan ROAS positif"},
        {"fase": "Bulan 5-6", "nama": "Data-Driven", "skill": ["Google Analytics 4", "A/B Testing", "Marketing Automation"], "kursus": "Google Analytics Certification (Google — Gratis)", "milestone": "Certified Google Analytics + laporan performa campaign"},
    ],
    "Social Media Specialist": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Canva", "Copywriting", "Content Planning", "Instagram/TikTok"], "kursus": "HubSpot Social Media Marketing (HubSpot — Gratis)", "milestone": "Buat konten plan 1 bulan + eksekusi"},
        {"fase": "Bulan 3-4", "nama": "Analytics & Growth", "skill": ["Meta Business Suite", "Instagram Insights", "Hootsuite"], "kursus": "Meta Blueprint — Social Media Marketing (Meta — Gratis)", "milestone": "Analisis performa konten dan tumbuhkan followers organik"},
        {"fase": "Bulan 5-6", "nama": "Strategy", "skill": ["Paid Social", "Influencer Outreach", "Crisis Management"], "kursus": "Meta Blueprint Certified (Meta)", "milestone": "Portofolio kelola akun brand dengan data pertumbuhan"},
    ],
    "Content Creator": [
        {"fase": "Bulan 1-2", "nama": "Fondasi Konten", "skill": ["CapCut/Premiere", "Storytelling", "Canva", "Scripting"], "kursus": "YouTube Creator Academy (YouTube — Gratis)", "milestone": "10 video pertama dengan engagement rate positif"},
        {"fase": "Bulan 3-4", "nama": "Growth", "skill": ["SEO YouTube/TikTok", "Thumbnail Design", "Analytics"], "kursus": "TikTok Creator Academy (TikTok — Gratis)", "milestone": "1.000 subscriber/follower pertama"},
        {"fase": "Bulan 5-6", "nama": "Monetisasi", "skill": ["Brand Collaboration", "Personal Branding", "Content Strategy"], "kursus": "Creator Economy Resources (komunitas + mentoring)", "milestone": "Kolaborasi brand pertama atau monetisasi aktif"},
    ],
    "SEO Specialist": [
        {"fase": "Bulan 1-2", "nama": "SEO Dasar", "skill": ["Keyword Research", "On-Page SEO", "Google Search Console"], "kursus": "HubSpot SEO Certification (HubSpot — Gratis)", "milestone": "Optimasi 10 halaman website dan lihat kenaikan traffic"},
        {"fase": "Bulan 3-4", "nama": "Technical & Off-Page", "skill": ["Technical SEO", "Backlink Building", "Ahrefs/Semrush"], "kursus": "Ahrefs SEO Course (Ahrefs — Gratis)", "milestone": "Domain Authority naik dan ranking keyword target masuk halaman 1"},
        {"fase": "Bulan 5-6", "nama": "Advanced", "skill": ["SEO Strategy", "Programmatic SEO", "Local SEO"], "kursus": "Google Analytics Certification (Google — Gratis)", "milestone": "Case study SEO dengan data traffic sebelum-sesudah"},
    ],
    "Copywriter": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Copywriting Dasar", "Tata Bahasa", "Riset Target Audiens"], "kursus": "HubSpot Content Marketing (HubSpot — Gratis)", "milestone": "10 tulisan konten yang published di blog/medium"},
        {"fase": "Bulan 3-4", "nama": "Spesialisasi", "skill": ["SEO Writing", "Email Copywriting", "UX Writing"], "kursus": "Copyblogger Free Resources (copyblogger.com)", "milestone": "1 email campaign dengan open rate di atas rata-rata industri"},
        {"fase": "Bulan 5-6", "nama": "Portofolio", "skill": ["Brand Voice", "CRO Copywriting", "Long-form Content"], "kursus": "Google UX Design — Writing Module (Coursera)", "milestone": "Portofolio 20+ tulisan di berbagai format"},
    ],
    "Graphic Designer": [
        {"fase": "Bulan 1-2", "nama": "Fondasi Desain", "skill": ["Prinsip Desain", "Adobe Illustrator Dasar", "Canva Pro"], "kursus": "Canva Design School (Canva — Gratis)", "milestone": "10 karya desain di Behance"},
        {"fase": "Bulan 3-4", "nama": "Adobe Suite", "skill": ["Adobe Photoshop", "Illustrator Advanced", "Typography"], "kursus": "Adobe Creative Cloud Tutorials (Adobe — Gratis)", "milestone": "Brand identity lengkap (logo, guideline, mockup)"},
        {"fase": "Bulan 5-6", "nama": "Portfolio", "skill": ["Figma", "Motion Graphic Dasar", "Brand Identity"], "kursus": "Adobe Certified Professional (exam)", "milestone": "Portofolio Behance 20+ karya + first freelance client"},
    ],
    "Financial Analyst": [
        {"fase": "Bulan 1-2", "nama": "Fondasi", "skill": ["Excel Advanced", "Laporan Keuangan", "Akuntansi Dasar"], "kursus": "CFI Free Courses (corporatefinanceinstitute.com)", "milestone": "Bisa baca dan analisis laporan keuangan perusahaan publik"},
        {"fase": "Bulan 3-4", "nama": "Analisis Lanjut", "skill": ["Financial Modeling", "Valuasi DCF", "Power BI/Tableau"], "kursus": "Financial Modeling (CFI — beberapa modul gratis)", "milestone": "Financial model sederhana untuk 1 perusahaan"},
        {"fase": "Bulan 5-6", "nama": "Sertifikasi", "skill": ["CFA Level 1", "SQL Dasar", "Presentasi Data"], "kursus": "CFA Institute Free Resources (cfainstitute.org)", "milestone": "CFA Level 1 terdaftar + 1 investment thesis yang terdokumentasi"},
    ],
    "Admin E-Commerce": [
        {"fase": "Bulan 1-2", "nama": "Fondasi E-Commerce", "skill": ["Seller Center (Shopee/Tokopedia)", "Pengelolaan Pesanan", "Customer Chat"], "kursus": "Shopee Campus Program (Shopee — Gratis)", "milestone": "Bisa kelola toko online dengan response rate 100%"},
        {"fase": "Bulan 3-4", "nama": "Optimasi", "skill": ["Foto Produk Dasar", "Copywriting Produk", "Analisis Penjualan"], "kursus": "Tokopedia Academy (Tokopedia — Gratis)", "milestone": "Peningkatan conversion rate toko yang terukur"},
        {"fase": "Bulan 5-6", "nama": "Growth", "skill": ["Iklan Marketplace", "Multi-platform Management", "Data-driven Decisions"], "kursus": "Google Analytics (Google — Gratis)", "milestone": "Kelola 3+ marketplace dengan rating 4.8+ dan growth terdokumentasi"},
    ],
    "IT Support": [
        {"fase": "Bulan 1-2", "nama": "Fondasi Hardware & OS", "skill": ["Hardware Troubleshooting", "Windows/macOS Administration", "Printer Config"], "kursus": "Pelatihan Skillhub Kemnaker — e-training resmi gratis", "milestone": "Bisa merakit PC, install OS, dan troubleshooting hardware dasar"},
        {"fase": "Bulan 3-4", "nama": "Networking & Server", "skill": ["LAN/WLAN Setup", "IP Addressing", "DNS", "Active Directory"], "kursus": "Cisco Networking Basics (NetAcad)", "milestone": "Bisa setup jaringan lokal dan manage user di Active Directory"},
        {"fase": "Bulan 5-6", "nama": "IT Service Management", "skill": ["Ticketing System", "Customer Handling", "File Sharing"], "kursus": "Customer Service Training (HubSpot Academy — Gratis)", "milestone": "Simulasi penanganan tiket komplain dengan SLA yang baik"},
    ],
}


ROADMAP.update(_ROADMAP_EXTRA)