
# 🏥 AI-Powered Physiotherapy Exercise App (PyQt6)

An advanced AI-supported physiotherapy desktop application built using PyQt6.
The app guides users through exercises using tutorial videos, real-time camera monitoring,
pose tracking, rep counting, motion validation, and voice guidance.

---

## 🚀 Features

- ✅ Exercise tutorial system
- ✅ Real-time camera monitoring
- ✅ AI-based motion estimation
- ✅ Rep counter with live display
- ✅ Wrong motion detection (auto pause)
- ✅ Text-to-Speech guidance
- ✅ Circular loading progress animation
- ✅ API integration for saving exercise results
- ✅ Multi-page stacked UI design
- ✅ Clean modern UI with animations
- ✅ Exercise completion popup system

---

## 🧠 System Architecture

### Main Components

- PyQt6 GUI
- QMediaPlayer for video playback
- OpenCV-based camera processing (via worker thread)
- Pose estimation & motion analysis module
- CircularProgressBar custom widget
- Text-to-Speech thread handler
- API integration for saving exercise data

---

## 📂 Project Structure

```
physiotherapy_app/
│
├── main.py
├── modules/
│   ├── CaptureCameraFramesWorker.py
│   ├── videoApi.py
│   ├── CircularProgressBar.py
│   ├── TextToSpeechThread.py
│   ├── estimate_motion.py
│   └── exercise.py
│
├── media/
│   ├── background.png
│   ├── exercise videos (.mp4)
│   └── UI images
│
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```
git clone https://github.com/yourusername/ai-physiotherapy-app.git
cd ai-physiotherapy-app
```

### 2️⃣ Install Requirements

```
pip install PyQt6 opencv-python requests
```

---

## ▶️ Run Application

```
python main.py
```

---

## 🎥 How It Works

1. User logs in
2. Selects exercise from dropdown
3. Tutorial video plays
4. Camera activates
5. AI tracks movement
6. Counts repetitions
7. Detects wrong posture → auto pauses video
8. Exercise completion popup shown
9. Data saved to API

---

## 🔊 AI Functionalities

- Pose recognition
- Motion validation
- Rep counting
- Voice feedback
- Real-time camera feed display
- Exercise performance saving via API

---

## 📊 API Integration

Exercise data is sent to:

```
https://nutrianalyser.com:313/api/Exercise/SaveUserExerciseDetails
```

Payload example:

```
{
  "id": exercise_id,
  "userLoginID": user_id,
  "totalStep": total_steps,
  "currectStep": correct_steps,
  "totalTimeInMinute": time_spent
}
```

---

## 🔐 Production Notes

- Replace hardcoded token before deployment
- Secure API endpoints
- Add authentication validation
- Optimize camera thread performance
- Handle exceptions in worker threads

---

## 📈 Future Improvements

- Mediapipe or YOLO pose detection upgrade
- Cloud data storage
- User performance analytics dashboard
- Multi-user login system
- Export exercise report PDF
- Mobile version (Kivy / Flutter)

---

## 👨‍💻 Author

Developed as an AI-supported Physiotherapy Training Application using PyQt6.

---

⭐ If you find this project useful, give it a star on GitHub!
