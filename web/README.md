# NoF1 Web Dashboard

A modern React-based web dashboard for the NoF1 trading system, featuring user authentication, configuration management, and trading analytics.

## 🚀 Features

### ✅ Implemented
- **User Authentication**
  - User registration and login
  - JWT token management
  - Protected routes
  - Form validation

- **Modern UI**
  - Responsive design with Tailwind CSS
  - Dark/light theme support
  - Component-based architecture
  - Shadcn/ui components

- **State Management**
  - Zustand for global state
  - Persistent auth state
  - React Hook Form for forms

### 🚧 Coming Soon (Placeholders)
- Trading Dashboard
- Configuration Management
- Real-time Charts
- Portfolio Analytics
- Exchange Integration

## 🛠️ Tech Stack

- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + Shadcn/ui
- **State Management**: Zustand
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Icons**: Lucide React

## 📦 Installation

1. **Clone and navigate to the web directory**:
   ```bash
   cd /app/nof1/web
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

## 🔧 Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Configuration
VITE_API_URL=http://localhost:8000/api

# Environment
VITE_NODE_ENV=development
```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Button, Input, etc.)
│   ├── LoginForm.tsx   # Login form component
│   ├── RegisterForm.tsx # Registration form component
│   └── ProtectedRoute.tsx # Authentication wrapper
├── pages/              # Page components
│   ├── LoginPage.tsx   # Login page
│   ├── RegisterPage.tsx # Registration page
│   ├── DashboardPage.tsx # Main dashboard
│   └── ConfigPage.tsx  # Configuration page
├── stores/             # Zustand stores
│   └── authStore.ts    # Authentication state
├── lib/                # Utility functions and API
│   ├── api.ts          # API client
│   └── utils.ts        # Helper functions
├── types/              # TypeScript type definitions
│   ├── auth.ts         # Auth-related types
│   └── index.ts        # Type exports
├── routes/             # React Router configuration
│   └── index.tsx       # Route definitions
└── main.tsx            # App entry point
```

## 🔐 Authentication Flow

1. **Login**: User submits credentials → API validates → JWT stored → Redirect to dashboard
2. **Registration**: User creates account → API creates user → JWT stored → Redirect to dashboard
3. **Protected Routes**: All routes except `/login` and `/register` require authentication
4. **Auto-check**: App checks auth status on startup and redirect if needed

## 🎨 UI Components

The project uses Shadcn/ui components for a consistent design system:

- **Button**: Various styles and sizes
- **Input**: Form inputs with validation
- **Label**: Accessible form labels
- **Card**: Container components for content sections

## 🔄 API Integration

The frontend expects the following API endpoints:

```
POST /api/auth/login      - User login
POST /api/auth/register   - User registration
POST /api/auth/logout     - User logout
GET  /api/auth/me         - Get current user
```

The API client automatically adds JWT tokens to requests and handles 401 responses.

## 🛠️ Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run format       # Format code with Prettier
```

## 🧪 Development Notes

- The app uses **localStorage** for JWT token persistence
- **Zustand persist middleware** maintains auth state across page reloads
- **Form validation** is implemented with React Hook Form
- **Route protection** prevents unauthorized access to protected pages
- **API error handling** includes automatic logout on 401 responses

## 🎯 Next Steps

This is the initial framework. The following features are planned:

1. **Real Trading Dashboard**
   - Portfolio overview
   - Active positions
   - Trading history

2. **Configuration Management**
   - Exchange settings
   - Trading parameters
   - Risk management

3. **Real-time Features**
   - WebSocket connections
   - Live price updates
   - Trade notifications

4. **Advanced Analytics**
   - Performance charts
   - Risk metrics
   - Strategy backtesting

## 📝 License

This project is part of the NoF1 trading system.