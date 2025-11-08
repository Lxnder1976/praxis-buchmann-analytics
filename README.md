# Praxis Buchmann Analytics Dashboard

Ein intelligentes Analytics-Dashboard für praxis-buchmann.info mit KI-gestützten Handlungsempfehlungen und automatisierten Aktionen.

## 🎯 Projektübersicht

**Ziel**: Automatisiertes Dashboard zur Überwachung und Optimierung der Website-Performance mit Google Analytics, Search Console und Google Ads.

### ✨ Features
- 📊 **Real-time Analytics**: Google Analytics, Search Console & Google Ads Integration
- 🤖 **KI-Agent**: Claude SDK für automatisierte Handlungsempfehlungen
- ⚡ **FastAPI Backend**: Python-basierte API für Datenverarbeitung
- 🎨 **Next.js Frontend**: Modern React-basiertes Dashboard
- ☁️ **Azure Deployment**: Skalierbare Cloud-Infrastruktur

## 🏗️ Technologie-Stack

### Backend
- **Python 3.13** mit FastAPI
- **SQLAlchemy** für Datenpersistierung
- **Google APIs**: Analytics Data API, Search Console API, Google Ads API
- **Claude Agent SDK** für KI-Funktionalitäten

### Frontend (geplant)
- **Next.js 14+** mit TypeScript
- **shadcn/ui** + **Tailwind CSS**
- **Recharts** für Datenvisualisierung

### Infrastructure
- **Azure Container Apps** für Hosting
- **Azure SQL Database** für Datenspeicherung
- **Azure Functions** für Scheduled Tasks
- **Azure Key Vault** für Secrets Management

## 🚀 Getting Started

### Voraussetzungen
- Python 3.13+
- Google Analytics Property
- Google Cloud Console Zugang

### Installation

```bash
# Repository klonen
git clone https://github.com/Lxnder1976/praxis-buchmann-analytics.git
cd praxis-buchmann-analytics

# Python Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r backend/requirements.txt

# Environment konfigurieren
cp backend/.env.example backend/.env
# .env Datei mit Google Analytics Credentials bearbeiten
```

### Google Analytics Setup

1. **Google Cloud Console:**
   - Erstellen Sie ein Service Account
   - Aktivieren Sie die Google Analytics Data API
   - Laden Sie die JSON-Credentials herunter

2. **Google Analytics:**
   - Fügen Sie den Service Account als "Viewer" hinzu
   - Notieren Sie sich die Property ID

3. **Configuration:**
   ```bash
   # backend/.env
   GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id
   GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
   ```

### Tests ausführen

```bash
# API-Verbindung testen
python backend/test_service.py

# Entwicklungsserver starten
uvicorn backend.app.main:app --reload --port 8000
```

## 📊 API Endpoints

- `GET /` - Health Check
- `GET /health` - Detaillierter Gesundheitsstatus
- `POST /fetch-data?days_back=7` - Daten von Google Analytics abrufen
- `GET /data-summary` - Übersicht der gespeicherten Daten
- `POST /cleanup-data?days_to_keep=90` - Alte Daten bereinigen

## 🔄 Entwicklungsfortschritt

### ✅ Phase 1: Data Pipeline (Abgeschlossen)
- [x] Google Analytics API Integration
- [x] SQLAlchemy Database Models
- [x] FastAPI Backend Setup
- [x] Automatische Datenpersistierung
- [x] Comprehensive Testing

### 🔄 Phase 2: Frontend Dashboard (In Planung)
- [ ] Next.js App Setup
- [ ] shadcn/ui Integration
- [ ] Analytics Datenvisualisierung
- [ ] Real-time Updates

### 🔄 Phase 3: KI-Agent Integration (In Planung)
- [ ] Claude Agent SDK Integration
- [ ] Automated Insights Generation
- [ ] Action Recommendation System
- [ ] Natural Language Queries

### 🔄 Phase 4: Azure Deployment (In Planung)
- [ ] Azure Container Apps Setup
- [ ] CI/CD Pipeline (GitHub Actions)
- [ ] Production Database Migration
- [ ] Monitoring & Logging

## 🔐 Security

- Service Account Authentication für Google APIs
- Azure Key Vault für Secrets Management
- Rate Limiting für API Calls
- Audit Logs für alle Aktionen

## 📈 Aktueller Status

**✅ Google Analytics Data Pipeline funktioniert!**
- Erfolgreiche Verbindung zu Google Analytics
- Automatische Datenabfrage und -speicherung
- FastAPI Server läuft stabil
- Umfassende Tests implementiert

**Nächste Schritte:**
1. Frontend Dashboard entwickeln
2. Claude Agent Integration
3. Azure Deployment vorbereiten

## 🤝 Contributing

Dieses Projekt wird privat entwickelt für praxis-buchmann.info. 

## 📄 Lizenz

Privates Projekt - Alle Rechte vorbehalten.

## 📞 Kontakt

Bei Fragen zum Projekt wenden Sie sich an den Entwickler.