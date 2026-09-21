# 🌱 EcoAI – AI Waste Segregation Assistant

An AI-powered web application that helps users identify and properly segregate waste using image analysis.

## 🎯 Project Overview

Improper waste segregation is a common sustainability challenge. People often have difficulty identifying whether an item belongs to wet, dry/recyclable, hazardous, or other waste categories.

**EcoAI** allows users to upload an image of a waste item and uses AI to classify it and provide disposal guidance.

## 🌍 SDG Alignment

**SDG 12 – Responsible Consumption and Production**

The project aims to promote responsible waste segregation and improve awareness of sustainable waste management.

## ✨ Features

- 📷 Upload a waste image
- 🤖 AI-powered waste classification
- ♻️ Waste category identification
- 📊 Confidence indication
- 🗑️ Disposal guidance
- 🎨 Colour-coded category display
- ⚠️ Responsible AI guidance
- 🔄 Error handling and retry support

## 🧠 AI Technology

- **Google Gemini 3.6 Flash** – multimodal image analysis
- **Prompt Engineering** – guides AI classification
- **Structured JSON Output** – consistent AI responses
- **Flask** – Python web backend
- **HTML/CSS/JavaScript** – frontend

## 🤖 IBM Bob Integration

IBM Bob was incorporated during the development of EcoAI.

Bob was used for:

- Codebase analysis
- Project planning
- Feature planning
- Code implementation
- Debugging
- Testing and validation
- User experience refinement

## 🔄 How It Works

```text
User uploads waste image
        ↓
Flask receives image
        ↓
Gemini AI analyzes image
        ↓
Structured classification
        ↓
Waste category + confidence
        ↓
Disposal guidance shown to user

## 🧪 Prototype Testing

| Test Item | Classification |
|-----------|----------------|
| Banana peel | Wet / Organic |
| Plastic bottle | Dry / Recyclable |
| Duracell battery | Hazardous |

## 🛡️ Responsible AI

EcoAI provides AI-based guidance rather than an absolute waste-management decision.

Future versions can improve reliability through:

- Testing with more waste items
- Incorporating local waste-management rules
- Better handling of ambiguous images
- Improved classification reliability

## 💻 Installation

Clone the repository:

```bash
git clone https://github.com/slingwat/ai-waste-segregation-assistant.git
cd ai-waste-segregation-assistant