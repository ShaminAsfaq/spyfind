# How to Run Spyfind Server - Complete Step-by-Step Guide

## 🎯 What We Just Did

I just started the Spyfind server for you. Here's what happened:

### Step-by-Step Breakdown of What I Did:

1. **Checked if a server was already running** (so we don't start a duplicate)
2. **Started the server** using the correct command
3. **Verified it's working** by checking if it responds to requests

The server is now **RUNNING** and ready to use at: **http://localhost:8000**

---

## 🚀 How to Run the Server Yourself (Next Time)

### Method 1: The Simple Way (Recommended for Beginners)

This is the easiest method if you just want to start using Spyfind.

#### Step 1: Open Terminal

- **Mac/Linux:** Open Applications → Utilities → Terminal
- **Windows:** Open Command Prompt or PowerShell

#### Step 2: Go to the Spyfind Folder

Type this command and press Enter:

```bash
cd /Users/islamkastero/spyfind
```

You should see something like:
```
islamkastero@MacBook spyfind %
```

#### Step 3: Activate Virtual Environment

This "turns on" the special Python workspace we set up.

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal line:
```
(venv) islamkastero@MacBook spyfind %
```

If you see `(venv)`, you're good to go! ✅

#### Step 4: Start the Server

Copy and paste this command:

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Press Enter and wait. You should see output like:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**If you see this, the server is running!** 🎉

#### Step 5: Use the Server

Open your web browser and go to:

```
http://localhost:8000
```

You should see the Spyfind website!

---

## 🛑 How to Stop the Server

The server is running in your terminal. To stop it:

### Method 1: Using Your Keyboard (Easiest)

1. Click in the terminal window (where the server is running)
2. Press **Ctrl + C** (hold Ctrl and press C)

You should see:
```
^C
INFO:     Shutting down
INFO:     Shutdown complete
```

The server is now **STOPPED**. ✅

### Method 2: Using Another Terminal (If you need to keep it running)

If you want to keep the server running while doing other things:

1. **Open a NEW terminal window** (don't close the one with the server)
2. You can use the new terminal for other commands
3. The server keeps running in the first terminal

---

## 📝 Complete Command Reference

### Starting the Server (Full Command)

```bash
# First, activate virtual environment
source venv/bin/activate

# Then start the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### What Each Part Means:

| Part | Meaning |
|------|---------|
| `source venv/bin/activate` | Turn on the Python environment |
| `python3` | Use Python 3 |
| `-m uvicorn` | Use the Uvicorn server tool |
| `app.main:app` | Run the app from file `app/main.py` |
| `--host 0.0.0.0` | Make it accessible from your computer |
| `--port 8000` | Use port 8000 (where the server listens) |

### Stopping the Server:

```bash
Press Ctrl + C in the terminal where the server is running
```

---

## ✅ Step-by-Step Checklist

Follow this checklist every time you want to start the server:

- [ ] **Step 1:** Open Terminal
- [ ] **Step 2:** `cd /Users/islamkastero/spyfind`
- [ ] **Step 3:** `source venv/bin/activate` (should show `(venv)`)
- [ ] **Step 4:** `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] **Step 5:** Wait for "Uvicorn running on" message
- [ ] **Step 6:** Open browser to `http://localhost:8000`
- [ ] **Step 7:** See the Spyfind website! 🎉

To stop:
- [ ] Click in terminal
- [ ] Press `Ctrl + C`
- [ ] See "Shutdown complete"

---

## 🎬 Visual Example

Here's what your terminal should look like:

### Starting the Server:

```
islamkastero@MacBook spyfind % source venv/bin/activate
(venv) islamkastero@MacBook spyfind % python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
INFO:     Started server process [62152]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

🟢 **Server is now RUNNING!**

### Stopping the Server:

```
Press Ctrl + C

^C
INFO:     Shutting down
INFO:     Shutdown complete
(venv) islamkastero@MacBook spyfind %
```

🔴 **Server is now STOPPED!**

---

## 🐛 Common Issues & Solutions

### Issue: "No such file or directory"

**Problem:** You're not in the right folder

**Solution:**
```bash
# Make sure you're in the spyfind folder
cd /Users/islamkastero/spyfind

# Then try again
source venv/bin/activate
```

### Issue: "(venv)" doesn't appear

**Problem:** Virtual environment didn't activate

**Solution:**
```bash
# Try this instead (Mac/Linux)
source venv/bin/activate

# Windows users try:
venv\Scripts\activate

# If still doesn't work, try:
. venv/bin/activate
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Problem:** Dependencies not installed

**Solution:**
```bash
# Install dependencies (make sure venv is activated first!)
pip install -r requirements.txt
```

### Issue: "Address already in use"

**Problem:** Another server is using port 8000

**Solution 1: Use a different port**
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Then visit: `http://localhost:8001`

**Solution 2: Kill the existing server**
```bash
# Find and kill the process using port 8000
lsof -i :8000
# Note the PID number, then:
kill -9 [PID]
```

### Issue: "Port 8000 is already in use" (Windows)

**Solution:**
```bash
# Use a different port
python3 -m uvicorn app.main:app --port 8001
```

---

## 📚 Understanding the Server

### What is "localhost:8000"?

- **localhost** = Your own computer
- **8000** = The port number (like a door to the server)
- Together: `localhost:8000` means "my computer's port 8000"

### What is the Virtual Environment?

Think of it like a separate "room" for Python:
- It has its own installed tools
- It doesn't affect your main Python
- You activate it when you want to use Spyfind
- You deactivate it when you're done (just close the terminal)

### What is Uvicorn?

It's a web server that:
- Listens on port 8000
- Handles requests from your browser
- Runs the Spyfind application
- Stops when you press Ctrl+C

---

## 🎯 Quick Summary

| Action | Command |
|--------|---------|
| Go to project | `cd /Users/islamkastero/spyfind` |
| Activate Python environment | `source venv/bin/activate` |
| Start server | `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Open website | Open browser, go to `http://localhost:8000` |
| Stop server | Press `Ctrl + C` in terminal |

---

## 🚀 Quick Start (One-Liner Version)

If you want to do it all in one go, here's the condensed version:

```bash
cd /Users/islamkastero/spyfind && source venv/bin/activate && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This does all steps at once:
1. Goes to the folder
2. Activates virtual environment
3. Starts the server

Then open: `http://localhost:8000`

---

## 📖 What's Happening Behind the Scenes

When you run the server, here's what happens:

1. **Virtual Environment Activates** → Python "switches" to use Spyfind tools
2. **Uvicorn Starts** → A web server wakes up
3. **Database Connects** → The app connects to `spyfind.db`
4. **Server Listens** → Waits for requests on port 8000
5. **You Can Access It** → Your browser can talk to it at `localhost:8000`

When you press **Ctrl+C**:

1. **Signal Sent** → Ctrl+C tells the server to shut down
2. **Server Shuts Down Gracefully** → Closes database connections
3. **Process Ends** → The server stops
4. **Terminal Returns** → You can type new commands

---

## ✨ Pro Tips

### Tip 1: Keep Terminal Open

Keep the terminal window with the server running visible. This way:
- You can see if there are errors
- You know the server is still running
- You can quickly stop it (Ctrl+C)

### Tip 2: Use Two Terminals

1. **Terminal 1:** Run the server (leave it running)
2. **Terminal 2:** Use for other commands (like running tests)

### Tip 3: Check If Server is Running

Open another terminal and run:

```bash
curl http://localhost:8000/health
```

If you see `{"status":"healthy"}`, the server is running! ✅

### Tip 4: Access from Other Devices

Since we use `--host 0.0.0.0`, you can access it from:
- Your computer: `http://localhost:8000`
- Other computers on your network: `http://[YOUR_IP]:8000`

To find your IP:
```bash
# Mac/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

---

## 🎓 Learning Resources

To understand more about the technologies:

- **Uvicorn:** https://www.uvicorn.org/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html

---

## ✅ Verification Checklist

After starting the server, verify everything works:

- [ ] Terminal shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] Browser shows Spyfind website at `http://localhost:8000`
- [ ] You can search hashtags
- [ ] You can create tweets
- [ ] You can view user profiles

If all checked, your server is working perfectly! 🎉

---

## 🎯 Next Steps

Now that you know how to run the server:

1. **Try the website** - Search for hashtags, create tweets
2. **Read README.md** - Learn how everything works
3. **Try the API** - Use curl commands to interact with it
4. **Add your own data** - Create users and tweets

---

**You now know everything you need to run Spyfind!** 🚀

