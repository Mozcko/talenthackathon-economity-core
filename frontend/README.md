# Economity - Zero-Friction Financial Tracking

Economity is a modern, AI-powered financial management frontend designed to eliminate the friction of manual expense tracking. By leveraging GPT-4o and Whisper, users can log transactions through natural language, voice memos, or photos of receipts.

## 🚀 Features

### 1. Zero-Friction Logging (AI Powered)
*   **Voice-to-Transaction:** Record a quick audio (e.g., "Spent 50 dollars on dinner at Mario's") and let the system transcribe and categorize it automatically.
*   **Smart Vision:** Snap a photo of a ticket or receipt. The system extracts the vendor, amount, and date using GPT-4o Vision.
*   **Natural Language:** Type a quick sentence to log movements without filling out complex forms.

### 2. Behavioral Gamification
*   **XP & Levels:** Earn experience points for every transaction logged. Level up from Bronze to Mythic.
*   **Daily Streaks:** Maintain your tracking habit to build streaks and earn bonus XP.
*   **Achievements:** Unlock badges like "Honestidad Brutal" (logging a risky expense) or "Semana Perfecta".
*   **Next Milestone:** Real-time progress tracking toward your next financial level.

### 3. Smart Categorization
*   Automated mapping of AI-suggested categories to a structured catalog (Supervivencia, Crecimiento, Riesgo, etc.).
*   Risk detection for "Dopamine" spending (Gambling, alcohol, impulsive subscriptions).

### 4. Secure & Multi-tenant
*   Integrated with Clerk for secure authentication.
*   Zero-Trust architecture ensuring data is siloed by tenant UUID.

## 🛠️ Tech Stack

*   **Framework:** React / Next.js
*   **Styling:** Tailwind CSS
*   **Authentication:** Clerk Auth
*   **State Management:** (e.g., TanStack Query / SWR for API synchronization)
*   **Icons:** Lucide React

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/economity-frontend.git
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Configure Environment Variables:**
    Create a `.env.local` file:
    ```env
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
4.  **Run development server:**
    ```bash
    npm run dev
    ```

## 🔌 API Integration Points

The frontend interacts with the following core backend modules:

*   **`/upload`**: Endpoints for processing text, audio files, and images via AI agents.
*   **`/transacciones`**: CRUD operations for financial records, including specialized voice/image registration.
*   **`/gamificacion`**: Fetches user profiles, streaks, and achievement progress.
*   **`/categorias`**: Retrieves the full catalog of categories and subcategories for manual overrides.

## 🎨 UI Philosophy

*   **Mobile-First:** Designed for quick entry on the go.
*   **Feedback Loops:** Visual celebrations (confetti, XP bars) when transactions are logged to reinforce positive behavior.
*   **Transparency:** Clearly distinguish between "Essential" spending and "Risk" spending to promote financial awareness.

---
*Part of the Talent Hackathon Economity Core Project.*