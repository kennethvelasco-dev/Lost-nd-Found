# System Architecture

The Campus Lost and Found application follows a modern, decoupled architecture designed for scalability, security, and maintainability.

## 🏗️ Backend: Modular Flask

The backend utilizes the **Application Factory Pattern** ensuring that the app is highly configurable and testable.

### Layers
- **Routes**: Thin API controllers that handle HTTP requests and JSON responses.
- **Services**: The core business logic layer where validation, computations, and cross-model interactions occur.
- **Models**: Data access layer utilizing a repository-like pattern for interaction with the SQLite database.
- **Utils**: Shared helper functions for response formatting, input validation, and security auditing.

### Security
- **Authentication**: JWT-based auth with short-lived access tokens (15 mins) and long-lived refresh tokens (7 days).
- **Hardening**: Refresh Token Rotation (RTR) on every use, HTTP-only cookies for storage, and strict SameSite policies.
- **Rate Limiting**: Applied to sensitive endpoints (Login, Submission) to prevent brute-force attacks.

## 🎨 Frontend: React + Vite

The frontend is built for speed and visual excellence, utilizing a component-based architecture.

### Key Components
- **State Management**: Local and global state (React Context/Hooks) for user sessions and item filtering.
- **Styling**: Curated Vanilla CSS for a premium, custom-branded look.
- **Performance**: Vite-powered build system with optimized asset loading.

## 🗃️ Database Schema

The system uses SQLite for simplicity and portability, with the following core entities:
- **Users**: Authentication, roles (User/Admin), and profiles.
- **Lost Items**: Detailed reports of items missing by users.
- **Found Items**: Detailed reports of items recovered on campus.
- **Claims**: Linking users to found items with verification scores.
- **Audit Logs**: Comprehensive tracking of all administrative and security actions.
