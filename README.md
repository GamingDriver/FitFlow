# Login/Signup Forms - FastAPI + Tailwind CSS

## Project Structure

```
.
├── main.py                      # FastAPI app entry point
├── routes/
│   ├── __init__.py
│   ├── login.py                # Login routes (logic only)
│   └── signup.py               # Signup routes (logic only)
├── templates/
│   ├── login.html              # Login form HTML
│   └── signup.html             # Signup form HTML
├── static/
│   └── css/
│       └── style.css           # Shared CSS styles
├── requirements.txt            # Dependencies
└── README.md
```

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the server

```bash
python main.py
```

Server will run at: `http://127.0.0.1:8000`

### 3. Access pages

- **Login**: `http://127.0.0.1:8000/login-page`
- **Signup**: `http://127.0.0.1:8000/signup-page`

## Current State

✅ **Frontend**: HTML templates + separate CSS files (clean separation)
✅ **Backend Routes**: Login & Signup endpoints created as stubs
✅ **Tailwind CSS**: Dark purple/black gradient design
✅ **Proper Structure**: Python logic separated from HTML & CSS
❌ **NOT Connected**: Endpoints return stub responses (no DB logic yet)

## Files Architecture

### `main.py`

- FastAPI app initialization
- Static files mounted (`/static`)
- Routes included but **not connected**
- Home page redirects to login

### `routes/login.py`

- GET `/login-page` - Serves login template
- POST `/login` - **Stub endpoint** (TODO: Add DB logic)

### `routes/signup.py`

- GET `/signup-page` - Serves signup template
- POST `/signup` - **Stub endpoint** (TODO: Add DB logic)

### `templates/login.html` & `templates/signup.html`

- Clean, semantic HTML
- References CSS classes from `style.css`
- Zero embedded CSS or inline styles

### `static/css/style.css`

- Shared CSS utilities
- Input styles, button styles, text utilities
- Uses Tailwind CSS classes with `@apply`

## Design Features

- **Dark theme**: Gradient from `gray-950` → `purple-950`
- **Glassmorphism**: Backdrop blur with semi-transparent cards
- **Interactive inputs**: Purple border + glow on focus
- **Responsive**: Mobile-first, works on all screen sizes
- **Clean**: Minimal, timeless design

## Next Steps (When Ready)

1. Set up MySQL database
2. Add password hashing (bcrypt)
3. Implement actual signup logic (user creation, validation)
4. Implement actual login logic (password verification, sessions)
5. Add error handling & user feedback messages
6. Connect forms to working database endpoints
