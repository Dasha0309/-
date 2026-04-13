# dictionary.py

# ============================================================
# МОНГОЛ ТЕКСТ БОЛОВСРУУЛАЛТ
# ============================================================

# Нийтлэг дуудлагын алдаа → зөв хэлбэр
# (Azure-ийн өөрийн хэлний загвар алдааны дийлэнхийг зассан ч
#  нэмэлт нарийвчлалын давхарга болгон хэрэглэнэ)

# dictionary.py

MONGOLIAN_CORRECTIONS: dict[str, str] = {
    r"\bболхгүй\b":       "болохгүй",
    r"\bхийхгүй\b":       "хийхгүй",
    r"\bбайхгүй\b":       "байхгүй",
    r"\bүзхгүй\b":        "үзэхгүй",
    r"\bочхгүй\b":        "очихгүй",
    r"\bирхгүй\b":        "ирэхгүй",
    r"\bявхгүй\b":        "явахгүй",
    r"\bхэлхгүй\b":       "хэлэхгүй",
    r"\bгаргахгүй\b":     "гаргахгүй",
    r"\bавхгүй\b":        "авахгүй",
    r"\bхийсэн\sбайгаа\b": "хийгээд байгаа",
    r"\bюу гэсэн үг вэ\b": "гэсэн үг юу вэ",
}

TECHNICAL_MN_TO_EN: dict[str, str] = {
    # Blockchain / Web3
    r"\bблокчэйн\b":       "blockchain",
    r"\bхэш\b":            "hash",
    r"\bтранзакшн\b":      "transaction",
    r"\bсмарт контракт\b": "smart contract",
    r"\bтокен\b":          "token",
    r"\bвэб3\b":           "Web3",
    r"\bнод\b":            "node",
    r"\bвалет\b":          "wallet",
    
    # IT / Software
    r"\bапи\b":            "API",
    r"\bэй пи ай\b":       "API",
    r"\bай ти\b":          "IT",
    r"\bсолюшн\b":         "solution",
    r"\bбэкэнд\b":         "backend",
    r"\bфронтэнд\b":       "frontend",
    r"\bдата\b":           "data",
    r"\bсервер\b":         "server",
    r"\bклауд\b":          "cloud",
    r"\bдэплой\b":         "deploy",
    r"\bсофтвэйр\b":       "software",
    r"\bбаг\b":            "bug",
    
    # Business / Meeting
    r"\bмитинг\b":         "meeting",
    r"\bрепорт\b":         "report",
    r"\bдедлайн\b":        "deadline",
    r"\bпрожект\b":        "project",
    r"\bменежер\b":        "manager",
    r"\bтимлид\b":         "team lead",
    r"\bкейс\b":           "case",
    r"\bбюджет\b":         "budget",
    r"\bфидбэк\b":         "feedback",
    r"\bагенда\b":         "agenda",

    r"\bблокчэйн\b":       "blockchain",
    r"\bхэш\b":            "hash",
    r"\bтранзакшн\b":      "transaction",
    r"\bсмарт контракт\b": "smart contract",
    r"\bтокен\b":          "token",
    r"\bвэб гурав\b":      "Web3",
    r"\bвэб3\b":           "Web3",
    r"\bнод\b":            "node",
    r"\bвалет\b":          "wallet",
    
    # Мэдээллийн технологи (IT)
    r"\bапи\b":            "API",
    r"\bэй пи ай\b":       "API",
    r"\bай ти\b":          "IT",
    r"\bсолюшн\b":         "solution",
    r"\bбэкэнд\b":         "backend",
    r"\bфронтэнд\b":       "frontend",
    r"\bдата\b":           "data",
    r"\bдата бэйс\b":      "database",
    r"\bсервер\b":         "server",
    r"\bклауд\b":          "cloud",
    r"\bфрэймворк\b":      "framework",
    r"\bдэплой\b":         "deploy",
    r"\bдэвлопер\b":       "developer",
    r"\bсофтвэйр\b":       "software",
    r"\bхардвэйр\b":       "hardware",
    r"\bкод\b":            "code",
    r"\bкодинг\b":         "coding",
    r"\bсистем\b":         "system",
    r"\bинтерфэйс\b":      "interface",
    r"\bбөглөө\b":         "bug", # Програмчлалын алдааг 'баг' гэж хэлэх нь түгээмэл
    r"\bбаг\b":            "bug",
    r"\bапдейт\b":         "update",
    r"\bапгрейд\b":        "upgrade",

    # Бизнес / Удирдлага / Хурал
    r"\bмитинг\b":         "meeting",
    r"\bрепорт\b":         "report",
    r"\bдедлайн\b":        "deadline",
    r"\bпрожект\b":        "project",
    r"\bменежер\b":        "manager",
    r"\bтим\b":            "team",
    r"\bтимлид\b":         "team lead",
    r"\bкейс\b":           "case",
    r"\bбюджет\b":         "budget",
    r"\bстартап\b":        "startup",
    r"\bпрезентейшн\b":    "presentation",
    r"\bфидбэк\b":         "feedback",
    r"\bаналитик\b":       "analytics",
    r"\bкэш\b":            "cache",
    r"\bагенда\b":         "agenda",
    r"\bворкшоп\b":        "workshop",
    r"\bсэминар\b":        "seminar",
    r"\bвэбинар\b":        "webinar",
    r"\bпиар\b":           "PR",
    r"\bэйч ар\b":         "HR",
    r"\bбизнес модель\b":   "business model",
    r"\bнетворк\b":        "network",
    r"\bстратеги\b":       "strategy",
    r"\bинноваци\b":       "innovation",
    r"\bинвестмент\b":     "investment",
    r"\bпич\b":            "pitch",
    r"\bмилстоун\b":       "milestone",

    # Маркетинг / Борлуулалт
    r"\bмаркетинг\b":      "marketing",
    r"\bбрэнд\b":          "brand",
    r"\bконтент\b":        "content",
    r"\bтаргет\b":         "target",
    r"\bтраффик\b":        "traffic",
    r"\bкампанит ажил\b":   "campaign",
    r"\bсэйлс\b":          "sales",
    r"\bдижитал\b":        "digital",
    r"\bсошиал медиа\b":    "social media",

    # Бусад түгээмэл үгс
    r"\bскрипт\b":         "script",
    r"\bдокумент\b":       "document",
    r"\bформат\b":         "format",
    r"\bмониторинг\b":     "monitoring",
    r"\bлогистик\b":       "logistics",
    r"\bпроцесс\b":        "process",
}