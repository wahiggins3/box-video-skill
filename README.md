# 🎥 Box Video Skill

**AI-Powered Video Analysis and Transcription for Box**

A production-ready Box Custom Skill that automatically processes video and audio files with AI-powered transcription, summarization, and keyword extraction. When users upload media files to Box, this skill provides instant, comprehensive analysis displayed as interactive cards in the Box interface.

![Box Skills Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-Whisper%20%26%20GPT--4-purple)

## 🌟 Features

### 📋 **Four AI-Powered Cards**

1. **📝 Summary Card**
   - AI-generated 2-4 sentence overview
   - Powered by GPT-4 Turbo
   - Provides high-level content understanding

2. **🏷️ Keywords Card**
   - 5-10 relevant keywords and key phrases
   - Extracted using GPT-4 Turbo
   - Searchable terms and proper nouns

3. **📄 Transcript Card**
   - Full timestamped transcript
   - Powered by OpenAI Whisper
   - Interactive timeline integration
   - Click-to-seek video functionality

4. **🤖 AI Processing Details Card**
   - Service information and processing times
   - Performance metrics and efficiency data
   - File size, duration, and technical metadata

### ✨ **Technical Capabilities**

- **🎬 Multi-format Support**: Handles video and audio files automatically
- **⚡ High Performance**: Faster-than-real-time processing
- **🔄 Auto-conversion**: Converts video to audio using FFmpeg
- **🛡️ Robust Error Handling**: Graceful failures with informative error cards
- **📊 Comprehensive Logging**: Detailed processing information
- **☁️ Cloud Native**: Deployed on Google Cloud Run with auto-scaling

## 🛠 Technical Stack

- **Backend**: Python 3.9+ with Flask
- **AI Services**:
  - OpenAI Whisper (Audio transcription)
  - GPT-4 Turbo (Summary and keyword extraction)
- **Cloud Platform**: Google Cloud Run
- **Integration**: Box Skills API
- **Media Processing**: FFmpeg
- **Container**: Docker

## 🚀 Quick Start

### Prerequisites

- Box Custom Skill configured
- OpenAI API key
- Google Cloud account
- Docker (for local development)

### Environment Variables

Create a `.env` file (not tracked in git):

```bash
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/wahiggins3/box-video-skill.git
   cd box-video-skill
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Run locally**
   ```bash
   python main.py
   ```

### Cloud Deployment

Deploy to Google Cloud Run:

```bash
gcloud run deploy box-video-skill \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8080 \
  --memory=2Gi \
  --timeout=600 \
  --max-instances=10 \
  --set-env-vars="OPENAI_API_KEY=your-api-key"
```

## 📖 Usage

1. **Upload a video or audio file** to your Box folder
2. **Box automatically triggers** the webhook
3. **Processing begins** - file download, transcription, AI analysis
4. **Four cards appear** in the Box interface with comprehensive analysis

### Supported File Formats

- **Video**: MP4, MOV, AVI, MKV, WebM
- **Audio**: MP3, M4A, WAV, FLAC, OGG

## 🏗 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Box Upload    │───▶│  Webhook Trigger │───▶│ Cloud Run App   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 ▼                                 │
                       │                    ┌─────────────────────┐                       │
                       │                    │   File Download     │                       │
                       │                    │   (Box API)         │                       │
                       │                    └─────────────────────┘                       │
                       │                                 │                                 │
                       │                                 ▼                                 │
                       │                    ┌─────────────────────┐                       │
                       │                    │   Audio Conversion  │                       │
                       │                    │   (FFmpeg)          │                       │
                       │                    └─────────────────────┘                       │
                       │                                 │                                 │
                       │                 ┌───────────────┼───────────────┐                 │
                       │                 ▼               ▼               ▼                 │
                       │    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
                       │    │   Transcription │ │    Summary      │ │    Keywords     │   │
                       │    │ (OpenAI Whisper)│ │  (GPT-4 Turbo)  │ │  (GPT-4 Turbo)  │   │
                       │    └─────────────────┘ └─────────────────┘ └─────────────────┘   │
                       │                                 │                                 │
                       │                                 ▼                                 │
                       │                    ┌─────────────────────┐                       │
                       │                    │  Format & Upload    │                       │
                       │                    │   (Box Skills API)  │                       │
                       │                    └─────────────────────┘                       │
                       └─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
box-video-skill/
├── main.py                 # Flask webhook handler and main processing pipeline
├── skills_formatter.py     # Box Skills metadata formatting for all card types
├── whisper_client.py       # OpenAI Whisper integration with timing metrics
├── gpt_keywords.py         # GPT-4 summary and keyword extraction
├── box_client.py           # Box API file download functionality
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration for Cloud Run
├── Procfile               # Process configuration
├── backups/               # Working state backups with documentation
├── .gitignore            # Excludes sensitive files (.env, etc.)
└── README.md             # This file
```

## 🔧 Configuration

### Box Skills Setup

1. Create a **Box Custom Skill** in your Box Developer Console
2. Set the **Invocation URL** to your deployed Cloud Run service
3. Configure **Read** and **Write** permissions
4. Set **Supported File Extensions** for video/audio files

### OpenAI API

- Requires OpenAI API access with Whisper and GPT-4 capabilities
- Usage costs apply based on file duration and text length
- Typical cost: ~$0.10-0.50 per video depending on length

## 🔍 Monitoring & Debugging

The application provides comprehensive logging:

- **Processing steps** with timing information
- **API call details** and response codes
- **Error handling** with detailed error messages
- **Performance metrics** (efficiency vs real-time)

View logs in Google Cloud Console or use:
```bash
gcloud run logs read --service=box-video-skill --region=us-central1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

- [ ] Multi-language transcription support
- [ ] Custom keyword categories
- [ ] Sentiment analysis
- [ ] Speaker identification
- [ ] Chapter/section detection
- [ ] Custom summary lengths

## 📞 Support

For issues and questions:
- Create an [Issue](https://github.com/wahiggins3/box-video-skill/issues)
- Check the [Wiki](https://github.com/wahiggins3/box-video-skill/wiki) for detailed documentation

---

**Built with ❤️ for the Box ecosystem** 