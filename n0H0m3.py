import sys, random, re, numpy as np, requests, subprocess, os, time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QStackedLayout,
    QDialog, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty,
    QTimer, QRectF
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPainterPath, QPen, QBrush, QLinearGradient
)

# -----------------------------
# Global Build & Update Config
# -----------------------------
BUILD_VERSION = "v1.0.0"
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/master/version.txt"
UPDATE_EXE_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/master/n0H0m3.exe"
UPDATER_EXE_PATH = "updater.exe"  # This file will be in the same folder as your main EXE

# -----------------------------
# Helper: Color Blending Function
# -----------------------------
def blendColors(color1, color2, t):
    r = int(color1.red() * t + color2.red() * (1 - t))
    g = int(color1.green() * t + color2.green() * (1 - t))
    b = int(color1.blue() * t + color2.blue() * (1 - t))
    return QColor(r, g, b)

# -----------------------------
# Auto Update Functions for EXE
# -----------------------------
def perform_update_exe():
    """Downloads the new EXE and launches the updater."""
    print("Downloading new executable...")
    try:
        response = requests.get(UPDATE_EXE_URL)
        update_path = os.path.join(os.getcwd(), "update_temp.exe")
        with open(update_path, "wb") as f:
            f.write(response.content)
        print("Download complete. Launching updater...")
        # Launch the updater executable, passing the path to the downloaded new exe.
        subprocess.Popen([UPDATER_EXE_PATH, update_path])
    except Exception as e:
        print("Update failed:", e)
    sys.exit()  # Exit the current app so the updater can overwrite it.

def check_for_updates(parent=None):
    """Checks remote version and prompts user if an update is available."""
    try:
        remote_version = requests.get(REMOTE_VERSION_URL).text.strip()
        if remote_version != BUILD_VERSION:
            # Use the LightModeWarningDialog as the update prompt
            dialog = LightModeWarningDialog(parent)
            dialog.msg_label.setText(f"Update available: {remote_version}\nDo you want to update now?")
            dialog.proceed_btn.setText("Update Now")
            dialog.cancel_btn.setText("Later")
            if dialog.exec_() == QDialog.Accepted:
                perform_update_exe()
            else:
                print("Update postponed.")
        else:
            print("No update available.")
    except Exception as e:
        print("Failed to check for updates:", e)

# -----------------------------
# Custom Warning Dialog for Light Mode / Auto Update
# -----------------------------
class LightModeWarningDialog(QDialog):
    def __init__(self, parent=None):
        super(LightModeWarningDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #222222;
                border: 2px solid #FFD700;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
            }
            QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #FFD700;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        warning_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setStyleSheet("color: #FFD700;")
        warning_layout.addWidget(icon_label)
        self.msg_label = QLabel("Warning: You're about to flashbang yourself. Do you wish to proceed?")
        self.msg_label.setWordWrap(True)
        warning_layout.addWidget(self.msg_label)
        layout.addLayout(warning_layout)
        btn_layout = QHBoxLayout()
        self.proceed_btn = QPushButton("Proceed Retina-Delete")
        self.cancel_btn = QPushButton("Abort!")
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.proceed_btn)
        layout.addLayout(btn_layout)
        self.proceed_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

# -----------------------------
# Bit Snow Effect (Updated)
# -----------------------------
class BitSnowEffect(QWidget):
    def __init__(self, parent=None):
        super(BitSnowEffect, self).__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.bits = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBits)
        self.timer.start(30)
        self.maxBits = 150
        self.spawnChance = 0.3
        self.baseFont = QFont("Monospace", 12)
        self.baseFont.setStyleHint(QFont.TypeWriter)
    
    def showEvent(self, event):
        self.bits = []
        w = self.width()
        num_initial = 20
        for i in range(num_initial):
            new_bit = {
                "char": random.choice(["0", "1"]),
                "x": (w / num_initial) * i + random.uniform(0, w/num_initial),
                "y": random.uniform(-10, 10),
                "speed": random.uniform(0.5, 2.0),
                "opacity": 0.0,
                "size": random.uniform(0.8, 1.5),
                "angle": random.uniform(0, 360),
                "rotation_speed": random.uniform(-2, 2)
            }
            self.bits.append(new_bit)
        super(BitSnowEffect, self).showEvent(event)
    
    def updateBits(self):
        if self.width() <= 0:
            return
        height = self.height()
        for bit in self.bits:
            if bit["y"] < height * 0.1 and bit["opacity"] < 1:
                bit["opacity"] = min(1, bit["opacity"] + 0.05)
            deceleration = 0.5 + 0.5 * (1 - bit["y"] / height)
            bit["y"] += bit["speed"] * deceleration
            bit["angle"] += bit["rotation_speed"]
            fade_start = height * 0.7
            if bit["y"] > fade_start:
                bit["opacity"] = max(0, 1 - (bit["y"] - fade_start) / (height - fade_start))
        self.bits = [bit for bit in self.bits if bit["y"] < height and bit["opacity"] > 0]
        if len(self.bits) < self.maxBits and random.random() < self.spawnChance:
            new_bit = {
                "char": random.choice(["0", "1"]),
                "x": random.uniform(0, self.width()),
                "y": 0,
                "speed": random.uniform(0.5, 2.0),
                "opacity": 0.0,
                "size": random.uniform(0.8, 1.5),
                "angle": random.uniform(0, 360),
                "rotation_speed": random.uniform(-2, 2)
            }
            self.bits.append(new_bit)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.baseFont)
        for bit in self.bits:
            color = QColor("#222222")
            color.setAlphaF(bit["opacity"])
            painter.setPen(color)
            painter.save()
            painter.translate(int(bit["x"]), int(bit["y"]))
            painter.rotate(bit["angle"])
            painter.scale(bit["size"], bit["size"])
            rect = painter.fontMetrics().boundingRect(bit["char"])
            painter.drawText(int(-rect.width()/2), int(rect.height()/2), bit["char"])
            painter.restore()

# -----------------------------
# Particle Background for Main UI
# -----------------------------
class ParticleBackground(QWidget):
    def __init__(self, theme='light', parent=None):
        super(ParticleBackground, self).__init__(parent)
        self.theme = theme
        self.particles = []
        self.numParticles = 150
        self.initParticles()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateParticles)
        self.timer.start(30)
    
    def initParticles(self):
        self.particles = []
        w, h = self.width() or 800, self.height() or 600
        colors = [QColor("#000000"), QColor("#8B0000")] if self.theme == 'light' else [QColor("#FFFFFF"), QColor("#8B0000")]
        for _ in range(self.numParticles):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            r = random.uniform(1, 3)
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(-0.5, 0.5)
            color = random.choice(colors)
            self.particles.append({'x': x, 'y': y, 'r': r, 'dx': dx, 'dy': dy, 'color': color})
    
    def resizeEvent(self, event):
        self.initParticles()
        super(ParticleBackground, self).resizeEvent(event)
    
    def updateParticles(self):
        w, h = self.width(), self.height()
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            if p['x'] < 0 or p['x'] > w:
                p['dx'] *= -1
            if p['y'] < 0 or p['y'] > h:
                p['dy'] *= -1
        self.update()
    
    def setTheme(self, theme):
        self.theme = theme
        self.initParticles()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for p in self.particles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(p['color']))
            painter.drawEllipse(int(p['x']), int(p['y']), int(p['r']*2), int(p['r']*2))

# -----------------------------
# Toggle Switch (Unchanged)
# -----------------------------
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)
    def __init__(self, parent=None, width=60, height=28):
        super(ToggleSwitch, self).__init__(parent)
        self.setFixedSize(width, height)
        self._checked = False
        self._position = 0.0  
        self._animation = QPropertyAnimation(self, b"posValue")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
    @pyqtProperty(float)
    def posValue(self):
        return self._position
    @posValue.setter
    def posValue(self, value):
        self._position = value
        self.update()
    def mousePressEvent(self, event):
        self.toggle()
        super(ToggleSwitch, self).mousePressEvent(event)
    def toggle(self):
        self.setChecked(not self._checked)
    def setChecked(self, state):
        self._checked = state
        start_value = self._position
        end_value = self.width() - self.height() if self._checked else 0.0
        self._animation.stop()
        self._animation.setStartValue(start_value)
        self._animation.setEndValue(end_value)
        self._animation.start()
        self.toggled.emit(self._checked)
    def isChecked(self):
        return self._checked
    def paintEvent(self, event):
        radius = self.height() / 2
        circle_diameter = self.height() - 4  
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        active_color = QColor("#555555")
        inactive_color = QColor("#CCCCCC")
        bg_color = active_color if self._checked else inactive_color
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)
        if self._checked:
            dot_color = QColor("#333333")
            icon = "🌙"
        else:
            dot_color = QColor("#FFD700")
            icon = "☀"
        dot_x = int(self._position) + 2
        dot_y = 2
        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(dot_x, dot_y, circle_diameter, circle_diameter)
        icon_font = QFont("Arial", int(circle_diameter * 0.6))
        painter.setFont(icon_font)
        painter.setPen(QColor("white"))
        painter.drawText(dot_x, dot_y, circle_diameter, circle_diameter, Qt.AlignCenter, icon)

# -----------------------------
# Menu Option (Unchanged)
# -----------------------------
class MenuOption(QLabel):
    def __init__(self, text, parent=None):
        super(MenuOption, self).__init__(text, parent)
        self.setFont(QFont("Arial", 24))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: #CCCCCC; background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setActive(False)
    def setActive(self, active):
        if active:
            self.setStyleSheet("color: white; background: transparent;")
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 255, 0))
            shadow.setOffset(0)
            self.setGraphicsEffect(shadow)
        else:
            self.setStyleSheet("color: #CCCCCC; background: transparent;")
            self.setGraphicsEffect(None)
    def enterEvent(self, event):
        self.window().setActiveOption(self)
        super(MenuOption, self).enterEvent(event)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window().optionSelected(self)
        super(MenuOption, self).mousePressEvent(event)

# -----------------------------
# Startup Animation Overlay (Updated)
# -----------------------------
class StartupScreen(QWidget):
    animationFinished = pyqtSignal()
    def __init__(self, parent=None):
        super(StartupScreen, self).__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        if parent:
            self.setGeometry(parent.rect())
        self.particleBg = ParticleBackground(theme='dark', parent=self)
        self.particleBg.setGeometry(self.rect())
        self.particleBg.lower()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.animatedLabel = QLabel("", self)
        self.animatedLabel.setAlignment(Qt.AlignCenter)
        self.fontName = "Ubuntu"
        thinFont = QFont(self.fontName, 48, QFont.Light)
        self.animatedLabel.setFont(thinFont)
        self.animatedLabel.setStyleSheet("background: transparent; color: white;")
        self.animatedLabel.setAttribute(Qt.WA_TranslucentBackground)
        self.animatedLabel.setTextFormat(Qt.RichText)
        glow = QGraphicsDropShadowEffect(self.animatedLabel)
        glow.setBlurRadius(4)
        glow.setColor(QColor(255, 255, 255, 200))
        glow.setOffset(0)
        self.animatedLabel.setGraphicsEffect(glow)
        self.layout.addWidget(self.animatedLabel)
        self.messages = [
            "N0H0m3",
            "Welcome <span style='color:#FFD700;'>n0clu7ch</span>",
            "EXPECT US",
            "WE ARE AN0NYM0US",
            "WE ARE LEGI0N",
            "WE DO NOT FORGIVE",
            "WE DO NOT FORGET",
            "<span style='color:#8F0000;'>run</span>"
        ]
        self.currentMessageIndex = 0
        self.tokens = []
        self.tokenIndex = 0
        self.charIndex = 0
        self.cursorVisible = True
        self.cursorTimer = QTimer(self)
        self.cursorTimer.timeout.connect(self.blinkCursor)
        self.cursorTimer.setInterval(500)
        self.typeTimer = QTimer(self)
        self.typeTimer.timeout.connect(self.typeToken)
        self.typeTimer.setInterval(80)
        self.endTimer = QTimer(self)
        self.endTimer.setSingleShot(True)
        self.endTimer.setInterval(2000)
        self.endTimer.timeout.connect(self.animationFinished.emit)
        self.strobePhase = 0.0
        self.strobeTimer = QTimer(self)
        self.strobeTimer.timeout.connect(self.updateStrobe)
        self.strobeTimer.setInterval(50)
        self.heartbeat = []
        self.topHeartbeat = []
        self.hbTimer = QTimer(self)
        self.hbTimer.timeout.connect(self.updateHeartbeat)
        self.hbTimer.start(5)
        self.hbInitialized = False
    def updateStrobe(self):
        self.strobePhase += 0.5
        self.update()
    def startAnimation(self):
        self.currentMessageIndex = 0
        self.prepareTokens(self.messages[self.currentMessageIndex])
        self.typeTimer.start()
        self.cursorTimer.start()
        self.strobePhase = 0.0
        self.strobeTimer.start()
    def prepareTokens(self, message):
        self.tokens = re.split(r'(<[^>]+>)', message)
        self.tokenIndex = 0
        self.charIndex = 0
        self.currentMessage = ""
    def typeToken(self):
        if self.tokenIndex < len(self.tokens):
            token = self.tokens[self.tokenIndex]
            if token.startswith("<") and token.endswith(">"):
                self.currentMessage += token
                self.tokenIndex += 1
            else:
                if self.charIndex < len(token):
                    self.currentMessage += token[self.charIndex]
                    self.charIndex += 1
                else:
                    self.tokenIndex += 1
                    self.charIndex = 0
            self.updateLabel()
        else:
            self.typeTimer.stop()
            QTimer.singleShot(1000, self.advanceMessage)
    def advanceMessage(self):
        self.currentMessageIndex += 1
        if self.currentMessageIndex < len(self.messages):
            self.prepareTokens(self.messages[self.currentMessageIndex])
            self.typeTimer.start()
        else:
            self.cursorTimer.stop()
            self.typeTimer.stop()
            self.hbTimer.stop()
            self.strobeTimer.stop()
            self.endTimer.start()
    def blinkCursor(self):
        self.cursorVisible = not self.cursorVisible
        self.updateLabel()
    def updateLabel(self):
        cursor = "_" if self.cursorVisible else ""
        self.animatedLabel.setText(self.currentMessage + cursor)
    def updateHeartbeat(self):
        w, h = self.width(), self.height()
        if not self.hbInitialized or len(self.heartbeat) != w:
            baseline = int(h * 0.92)
            self.heartbeat = [baseline] * w
            self.hbBaseline = baseline
            self.hbAmplitude = int(h * 0.15)
        self.heartbeat.pop(0)
        if np.random.rand() < 0.1:
            new_val = self.hbBaseline - self.hbAmplitude - np.random.randint(0, 30)
        else:
            new_val = self.hbBaseline
        self.heartbeat.append(new_val)
        if not self.hbInitialized or len(self.topHeartbeat) != w:
            topBaseline = int(h * 0.08)
            self.topHeartbeat = [topBaseline] * w
            self.topHbBaseline = topBaseline
            self.topHbAmplitude = int(h * 0.1)
            self.hbInitialized = True
        self.topHeartbeat.pop(0)
        if np.random.rand() < 0.1:
            new_top = self.topHbBaseline + self.topHbAmplitude + np.random.randint(0, 20)
        else:
            new_top = self.topHbBaseline
        self.topHeartbeat.append(new_top)
        if self.currentMessageIndex == len(self.messages) - 1:
            self.strobePhase += 0.02
        self.update()
    def drawBarLights(self, painter):
        w, h = self.width(), self.height()
        bottomBaseline = self.hbBaseline if hasattr(self, 'hbBaseline') else int(h * 0.92)
        topBaseline = self.topHbBaseline if hasattr(self, 'topHbBaseline') else int(h * 0.08)
        bottomBarHeight = h - bottomBaseline
        topBarHeight = topBaseline
        factor = (np.sin(self.strobePhase) + 1) / 2
        bottomColor = blendColors(QColor(255, 0, 0), QColor(0, 0, 255), factor)
        bottomColor.setAlpha(180)
        topColor = blendColors(QColor(255, 0, 0), QColor(0, 0, 255), 1 - factor)
        topColor.setAlpha(180)
        gradBottom = QLinearGradient(0, bottomBaseline, 0, h)
        gradBottom.setColorAt(0, bottomColor)
        gradBottom.setColorAt(1, QColor(bottomColor.red(), bottomColor.green(), bottomColor.blue(), 0))
        painter.fillRect(0, bottomBaseline, w, bottomBarHeight, gradBottom)
        gradTop = QLinearGradient(0, 0, 0, topBaseline)
        gradTop.setColorAt(0, QColor(topColor.red(), topColor.green(), topColor.blue(), 0))
        gradTop.setColorAt(1, topColor)
        painter.fillRect(0, 0, w, topBarHeight, gradTop)
    def paintEvent(self, event):
        super(StartupScreen, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.hbInitialized and self.heartbeat:
            path = QPainterPath()
            path.moveTo(0, self.heartbeat[0])
            for x, y in enumerate(self.heartbeat):
                path.lineTo(x, y)
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.drawPath(path)
        if self.hbInitialized and self.topHeartbeat:
            rev = list(reversed(self.topHeartbeat))
            path_top = QPainterPath()
            path_top.moveTo(0, rev[0])
            for x, y in enumerate(rev):
                path_top.lineTo(x, y)
            pen_top = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen_top)
            painter.drawPath(path_top)
            offset_path = QPainterPath()
            offset_path.moveTo(0, rev[0] + 2)
            for x, y in enumerate(rev):
                offset_path.lineTo(x, y + 2)
            pen_offset = QPen(QColor(139, 0, 0), 2)
            painter.setPen(pen_offset)
            painter.drawPath(offset_path)
        if self.currentMessageIndex == len(self.messages) - 1:
            self.drawBarLights(painter)
    def fadeIntoMain(self):
        self.fadeAnim = QPropertyAnimation(self, b"windowOpacity")
        self.fadeAnim.setDuration(2000)
        self.fadeAnim.setStartValue(1)
        self.fadeAnim.setEndValue(0)
        self.fadeAnim.setEasingCurve(QEasingCurve.OutCubic)
        self.fadeAnim.finished.connect(self.animationFinished.emit)
        self.fadeAnim.start()

# -----------------------------
# Main Application Window (Updated Layout)
# -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("n0H0m3")
        self.showFullScreen()
        self.dark_mode = True
        container = QWidget(self)
        self.stack = QStackedLayout(container)
        self.setCentralWidget(container)
        # Main UI Page with Particle Background
        self.mainUI = QWidget()
        self.mainUI.setStyleSheet("background-color: #000000;")
        self.particleBg = ParticleBackground(theme='dark', parent=self.mainUI)
        self.particleBg.setGeometry(self.mainUI.rect())
        self.uiStack = QStackedLayout(self.mainUI)
        self.uiStack.setStackingMode(QStackedLayout.StackAll)
        self.uiStack.addWidget(self.particleBg)
        self.bitRain = BitSnowEffect(self.mainUI)
        self.bitRain.setGeometry(self.mainUI.rect())
        self.uiStack.addWidget(self.bitRain)
        # Content Widget with Header and Options
        self.contentWidget = QWidget()
        contentLayout = QVBoxLayout(self.contentWidget)
        contentLayout.setContentsMargins(0, 20, 0, 40)
        contentLayout.addStretch()
        self.header = QLabel("n0H0m3", self)
        self.header.setFont(QFont("Arial", 48, QFont.Bold))
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("color: white; background: transparent;")
        self.header.setAttribute(Qt.WA_TranslucentBackground)
        new_shadow = QGraphicsDropShadowEffect(self)
        new_shadow.setBlurRadius(40)
        new_shadow.setOffset(0)
        new_shadow.setColor(QColor(255, 255, 255))
        self.header.setGraphicsEffect(new_shadow)
        self.header_shadow = new_shadow
        contentLayout.addWidget(self.header)
        contentLayout.addSpacing(10)
        self.optionsContainer = QWidget()
        optionsLayout = QVBoxLayout(self.optionsContainer)
        optionsLayout.setAlignment(Qt.AlignHCenter)
        optionsLayout.setSpacing(40)
        self.menu_options = []
        for text in ["Open ktuner", "Settings", "Shutdown"]:
            option = MenuOption(text, self)
            self.menu_options.append(option)
        optionsLayout.addWidget(self.menu_options[0])
        optionsLayout.addWidget(self.menu_options[1])
        contentLayout.addWidget(self.optionsContainer)
        contentLayout.addStretch()
        contentLayout.addWidget(self.menu_options[2])
        self.navPrompt = QLabel("Navigate with ↑ ↓", self)
        self.navPrompt.setFont(QFont("Arial", 12))
        self.navPrompt.setStyleSheet("color: white; background: transparent;")
        self.navPrompt.setAlignment(Qt.AlignCenter)
        contentLayout.addWidget(self.navPrompt)
        self.selected_index = 0
        self.updateSelection()
        self.setupAnimation()
        self.uiStack.addWidget(self.contentWidget)
        self.dark_toggle = ToggleSwitch(self)
        self.dark_toggle.setChecked(True)
        self.dark_toggle.toggled.connect(self.toggleDarkMode)
        self.dark_toggle.show()
        self.dark_toggle.raise_()
        self.stack.addWidget(self.mainUI)
        self.startup = StartupScreen(self)
        self.startup.animationFinished.connect(self.fadeIntoMain)
        self.stack.addWidget(self.startup)
        self.stack.setCurrentWidget(self.startup)
        self.startup.startAnimation()
        # Build version label at bottom right
        self.buildVersionLabel = QLabel(BUILD_VERSION, self)
        self.buildVersionLabel.setStyleSheet("color: #888888; background: transparent; font-size: 10px;")
        self.buildVersionLabel.adjustSize()
        self.buildVersionLabel.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.buildVersionLabel.show()
    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        if hasattr(self, 'dark_toggle'):
            margin = 20
            ts_width = self.dark_toggle.width()
            ts_height = self.dark_toggle.height()
            self.dark_toggle.move((self.width() - ts_width) // 2,
                                  self.height() - ts_height - margin)
        if hasattr(self, 'particleBg'):
            self.particleBg.setGeometry(self.mainUI.rect())
        if hasattr(self, 'bitRain'):
            self.bitRain.setGeometry(self.mainUI.rect())
        self.buildVersionLabel.move(self.width() - self.buildVersionLabel.width() - 10,
                                    self.height() - self.buildVersionLabel.height() - 10)
    def setupAnimation(self):
        self.opacity_effect = QGraphicsOpacityEffect(self.header)
        self.header.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(2000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()
    def updateSelection(self):
        for i, option in enumerate(self.menu_options):
            option.setActive(i == self.selected_index)
    def setActiveOption(self, option):
        if option in self.menu_options:
            self.selected_index = self.menu_options.index(option)
            self.updateSelection()
    def optionSelected(self, option):
        print(f"Selected: {option.text()}")
        if option.text().lower() == "shutdown":
            QApplication.quit()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
            self.updateSelection()
        elif event.key() == Qt.Key_Down:
            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
            self.updateSelection()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.optionSelected(self.menu_options[self.selected_index])
        else:
            super(MainWindow, self).keyPressEvent(event)
    def toggleDarkMode(self, state):
        if not state:
            dialog = LightModeWarningDialog(self)
            dialog.move(self.geometry().center() - dialog.rect().center())
            result = dialog.exec_()
            if result != QDialog.Accepted:
                self.dark_toggle.setChecked(True)
                return
        self.dark_mode = bool(state)
        if self.dark_mode:
            self.mainUI.setStyleSheet("background-color: #000000;")
            self.particleBg.setTheme('dark')
            new_shadow = QGraphicsDropShadowEffect(self)
            new_shadow.setBlurRadius(40)
            new_shadow.setOffset(0)
            new_shadow.setColor(QColor(255, 255, 255))
            self.header.setGraphicsEffect(new_shadow)
            self.header_shadow = new_shadow
        else:
            self.mainUI.setStyleSheet("background-color: #F0F0F0;")
            self.particleBg.setTheme('light')
            new_shadow = QGraphicsDropShadowEffect(self)
            new_shadow.setBlurRadius(40)
            new_shadow.setOffset(0)
            new_shadow.setColor(QColor(255, 255, 255, 180))
            self.header.setGraphicsEffect(new_shadow)
            self.header_shadow = new_shadow
    def fadeIntoMain(self):
        self.fadeAnim = QPropertyAnimation(self.startup, b"windowOpacity")
        self.fadeAnim.setDuration(2000)
        self.fadeAnim.setStartValue(1)
        self.fadeAnim.setEndValue(0)
        self.fadeAnim.setEasingCurve(QEasingCurve.OutCubic)
        self.fadeAnim.finished.connect(self.showMainUI)
        self.fadeAnim.start()
    def showMainUI(self):
        self.stack.setCurrentWidget(self.mainUI)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Check for updates before starting main window; prompt user if needed.
    check_for_updates()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
