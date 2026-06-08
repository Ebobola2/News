import os
import re
import pickle
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "classifier.pkl")

TRAINING_DATA = [
    ("Apple releases new iPhone with AI features", "технологии"),
    ("Google announces updates to Search algorithm", "технологии"),
    ("OpenAI launches new language model", "технологии"),
    ("Meta introduces mixed reality headset Vision Pro", "технологии"),
    ("Tesla releases full self-driving software update", "технологии"),
    ("Microsoft integrates AI Copilot into Office suite", "технологии"),
    ("Startup raises million funding for new AI product", "технологии"),
    ("New programming language gains popularity among developers", "технологии"),
    ("Cybersecurity breach exposes millions of user records", "технологии"),
    ("Show HN I built a new developer tool for productivity", "технологии"),
    ("The Verge reviews latest smartphone flagship camera test", "технологии"),
    ("New open source framework released on GitHub stars", "технологии"),
    ("Cloud provider AWS announces new pricing model services", "технологии"),
    ("Ask HN what is the best tech stack for web apps", "технологии"),
    ("Samsung unveils foldable phone with improved display", "технологии"),
    ("Amazon launches new Alexa voice assistant upgrade", "технологии"),
    ("Nvidia GPU shortage continues amid AI boom demand", "технологии"),
    ("Apple Vision Pro spatial computing headset review", "технологии"),
    ("Linux kernel 6.0 released with major performance improvements", "технологии"),
    ("Python overtakes JavaScript as most popular language survey", "технологии"),
    ("Browser extension blocks AI-generated content on websites", "технологии"),
    ("Anthropic releases Claude AI assistant new version update", "технологии"),
    ("ChatGPT reaches 100 million users milestone OpenAI", "технологии"),
    ("Elon Musk launches new AI company xAI Grok chatbot", "технологии"),
    ("Electric vehicle battery breakthrough extends range miles", "технологии"),
    ("Deepfake detection tool released by researchers university", "технологии"),
    ("Tech layoffs continue across Silicon Valley companies cut jobs", "технологии"),
    ("iPhone production shifts away from China manufacturing", "технологии"),
    ("Social media platform bans AI-generated fake accounts", "технологии"),
    ("Quantum computing milestone achieved by IBM researchers", "технологии"),

    ("Scientists discover new species of deep sea creature ocean", "наука"),
    ("NASA confirms liquid water beneath Mars polar ice cap", "наука"),
    ("Researchers develop quantum computer that breaks encryption", "наука"),
    ("New cancer immunotherapy achieves complete remission clinical trials", "наука"),
    ("Astronomers detect gravitational waves from neutron star collision", "наука"),
    ("DNA analysis reveals unknown branch of human evolution fossil", "наука"),
    ("Scientists achieve nuclear fusion net energy gain milestone", "наука"),
    ("Black hole merger photographed for first time in history telescope", "наука"),
    ("CRISPR gene therapy cures hereditary blindness in patients", "наука"),
    ("Deep ocean expedition discovers hydrothermal vent ecosystem", "наука"),
    ("Paleontologists unearth complete dinosaur skeleton in Patagonia", "наука"),
    ("Brain-computer interface allows paralyzed patient to walk again", "наука"),
    ("Physicists create new state of matter at ultra-low temperatures", "наука"),
    ("Solar telescope captures highest resolution images of sun surface", "наука"),
    ("Antibiotic-resistant bacteria defeated by new molecular compound", "наука"),
    ("James Webb telescope captures image of distant galaxy formation", "наука"),
    ("Climate scientists warn of accelerating ice sheet collapse", "наука"),
    ("New vaccine shows promise against malaria in Africa trials", "наука"),
    ("Researchers map complete human brain neural connections atlas", "наука"),
    ("Exoplanet discovered with atmosphere similar to Earth conditions", "наука"),
    ("Study finds microplastics in human blood for the first time", "наука"),
    ("SpaceX successfully lands rocket booster for reuse mission", "наука"),
    ("Obesity drug Wegovy reduces heart attack risk study finds", "наука"),
    ("Ancient DNA extracted from mammoth reveals new species lineage", "наука"),
    ("Ocean temperatures hit record high threatening coral reefs", "наука"),

    ("US Congress passes new budget spending bill debt ceiling", "политика"),
    ("President Biden signs executive order on immigration policy", "политика"),
    ("UK Prime Minister announces general election date vote", "политика"),
    ("European Union approves new AI regulation law parliament", "политика"),
    ("United Nations Security Council meets over conflict crisis", "политика"),
    ("Senate confirms new Supreme Court justice nomination vote", "политика"),
    ("Russia Ukraine war ceasefire negotiations latest update", "политика"),
    ("NATO alliance announces new defense spending commitments", "политика"),
    ("China Taiwan tensions rise amid military exercises drills", "политика"),
    ("French president Emmanuel Macron wins reelection vote", "политика"),
    ("US election results swing state count presidential race", "политика"),
    ("Government shutdown averted Congress last minute deal", "политика"),
    ("G7 summit leaders agree on new sanctions package", "политика"),
    ("Israel Gaza conflict ceasefire talks latest news update", "политика"),
    ("Boris Johnson resigns as UK Prime Minister scandal", "политика"),
    ("Iran nuclear deal talks resume Vienna negotiations", "политика"),
    ("India Modi wins landslide victory national election results", "политика"),
    ("Trump indicted on federal charges court case latest", "политика"),
    ("Climate deal signed at COP summit emissions targets", "политика"),
    ("Brazil Lula da Silva wins presidential election runoff", "политика"),
    ("Protest demonstration thousands march capital city streets", "политика"),
    ("Immigration crisis border policy debate government response", "политика"),
    ("Afghanistan Taliban government international recognition", "политика"),
    ("Sanctions imposed on country over human rights violations", "политика"),
    ("Prime minister faces vote of no confidence parliament", "политика"),

    ("Federal Reserve raises interest rates to fight inflation", "экономика"),
    ("Stock market falls amid recession fears Wall Street", "экономика"),
    ("Unemployment rate drops to lowest level in years", "экономика"),
    ("Oil prices surge after OPEC cuts production quota", "экономика"),
    ("Bitcoin cryptocurrency reaches new all-time high price", "экономика"),
    ("Amazon quarterly earnings beat analyst expectations revenue", "экономика"),
    ("Bank collapse triggers financial market panic investors", "экономика"),
    ("Inflation rate falls to two percent target central bank", "экономика"),
    ("Global supply chain disruption shipping costs rise", "экономика"),
    ("IMF lowers global growth forecast recession warning", "экономика"),
    ("Housing market slowdown mortgage rates affordability crisis", "экономика"),
    ("Microsoft acquires Activision Blizzard billion deal approved", "экономика"),
    ("Layoffs tech companies thousands jobs cut restructuring", "экономика"),
    ("Dollar strengthens against euro yen currency exchange", "экономика"),
    ("Apple becomes first company reach three trillion market cap", "экономика"),
    ("Trade war tariffs imposed goods imports exports affected", "экономика"),
    ("Startup unicorn IPO stock market listing valuation", "экономика"),
    ("Wages rise workers strike demand higher pay union", "экономика"),
    ("Energy prices spike gas electricity bills household costs", "экономика"),
    ("China economy slowdown property market debt crisis", "экономика"),

    ("World Cup final Argentina beats France penalty shootout", "спорт"),
    ("Champions League final Liverpool wins trophy goal", "спорт"),
    ("NBA Finals results score game seven overtime", "спорт"),
    ("Wimbledon tennis championship Novak Djokovic wins title", "спорт"),
    ("Super Bowl Kansas City Chiefs defeat Eagles score", "спорт"),
    ("Formula One Grand Prix race results standings season", "спорт"),
    ("Olympic Games Paris 2024 medal table results ceremony", "спорт"),
    ("Premier League Manchester City wins title championship", "спорт"),
    ("Tour de France cycling race stage winner mountain", "спорт"),
    ("UFC fight night knockout result champion defended", "спорт"),
    ("Transfer window footballer signs record fee contract", "спорт"),
    ("Cricket Test match England Australia Ashes series", "спорт"),
    ("Marathon world record broken athletics championship", "спорт"),
    ("Golf Masters tournament Augusta winner leaderboard", "спорт"),
    ("Rugby World Cup final South Africa wins trophy", "спорт"),

    ("Team Liquid wins Dota 2 International championship esports", "киберспорт"),
    ("CS2 Major tournament prize pool reaches record high esports", "киберспорт"),
    ("League of Legends World Championship finals viewers Twitch", "киберспорт"),
    ("Esports organization signs star player for record salary", "киберспорт"),
    ("Valorant Champions Tour announces new regional leagues Riot", "киберспорт"),
    ("Professional gamer retires after decade in competitive scene", "киберспорт"),
    ("StarCraft 2 tournament celebrates competitive gaming history", "киберспорт"),
    ("Overwatch League team acquires top Korean roster players", "киберспорт"),
    ("Fortnite World Cup crowns new champion grand final prize", "киберспорт"),
    ("Mobile esports market surpasses PC gaming in Asia revenue", "киберспорт"),
    ("ESL announces new Counter-Strike tournament format schedule", "киберспорт"),
    ("Twitch streamer banned platform rules violation community", "киберспорт"),
    ("Gaming YouTuber reaches 50 million subscribers milestone", "киберспорт"),
    ("New video game release breaks sales record first week", "киберспорт"),
    ("Esports arena opens new venue capacity crowd tickets", "киберспорт"),

    ("Pentagon tests hypersonic missile capable Mach speed defense", "военные технологии"),
    ("US Army deploys AI-powered autonomous combat drone swarm", "военные технологии"),
    ("New stealth destroyer equipped railgun enters naval service", "военные технологии"),
    ("DARPA develops exoskeleton suit for infantry soldiers field", "военные технологии"),
    ("Fifth generation fighter jet breaks performance records flight", "военные технологии"),
    ("Laser weapon system successfully intercepts ballistic missile", "военные технологии"),
    ("Military satellite network provides real-time battlefield intelligence", "военные технологии"),
    ("Nuclear submarine receives upgraded sonar torpedo systems", "военные технологии"),
    ("Electronic warfare system jams enemy communications range", "военные технологии"),
    ("Combat robot passes autonomous field operations evaluation test", "военные технологии"),
    ("Next-generation body armor stops armor-piercing rounds tests", "военные технологии"),
    ("Underwater drone extended autonomous patrol naval missions", "военные технологии"),
    ("Directed energy weapon destroys multiple targets simultaneously", "военные технологии"),
    ("Military AI system predicts enemy movements accuracy percent", "военные технологии"),
    ("Defense contractor awarded billion contract new weapons system", "военные технологии"),

    ("WHO declares new pandemic health emergency global outbreak", "здоровье"),
    ("COVID vaccine booster dose recommended elderly population", "здоровье"),
    ("Mental health crisis among young people social media study", "здоровье"),
    ("New drug approved FDA treatment Alzheimer disease patients", "здоровье"),
    ("Hospital waiting times reach record high NHS crisis", "здоровье"),
    ("Diet study links ultra-processed food cancer risk health", "здоровье"),
    ("Exercise reduces dementia risk new research study finds", "здоровье"),
    ("Antibiotic resistance growing threat global health warning", "здоровье"),
    ("Sleep deprivation linked heart disease study research", "здоровье"),
    ("New treatment breakthrough for Type 2 diabetes patients", "здоровье"),
    ("Mpox outbreak spreads countries WHO health alert", "здоровье"),
    ("Smoking rates decline young people vaping e-cigarettes", "здоровье"),
    ("Medical AI detects cancer earlier than doctors scan", "здоровье"),
    ("Obesity epidemic costs healthcare system billions year", "здоровье"),
    ("Flu season early start hospitals prepare surge patients", "здоровье"),
]


def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Zа-яёА-ЯЁ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            preprocessor=preprocess_text,
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=3.0,
            solver="lbfgs",
        )),
    ])


def train_model() -> Pipeline:
    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, zero_division=0)
    logger.info(f"Отчёт классификатора:\n{report}")
    print(report)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    logger.info(f"Модель сохранена: {MODEL_PATH}")
    return pipeline


def load_model() -> Pipeline:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    logger.info("Файл модели не найден — обучаем новую модель...")
    return train_model()


def predict_category(text: str, model: Pipeline = None) -> str:
    if model is None:
        model = load_model()
    cleaned = preprocess_text(text)
    if not cleaned:
        return "общее"
    prediction = model.predict([cleaned])[0]
    return prediction


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
        print("Старая модель удалена, переобучаем...")

    print("=== Обучение классификатора ===")
    model = train_model()

    tests = [
        "Apple launches new MacBook Pro with M3 chip",
        "Scientists discover new exoplanet with atmosphere",
        "Army deploys new hypersonic missile system",
        "Dota 2 tournament breaks viewer records on Twitch",
        "CRISPR therapy reverses genetic disease in patients",
        "Federal Reserve raises interest rates inflation fight",
        "World Cup final Argentina beats France",
        "WHO warns of new virus outbreak health emergency",
        "Trump Biden election results swing states count",
        "Show HN I built a tool for developers GitHub",
    ]
    print("\n=== Тест классификации ===")
    for t in tests:
        cat = predict_category(t, model)
        print(f"  {cat:25} | {t}")