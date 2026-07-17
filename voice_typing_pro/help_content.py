from __future__ import annotations

from html import escape

from . import APP_DISPLAY_NAME, DEVELOPER_NAME, PORTFOLIO_URL


def guide_html(language: str) -> str:
    if language == "en":
        return _english_guide()
    return _bengali_guide()


def developer_html(language: str) -> str:
    if language == "en":
        return _english_developer()
    return _bengali_developer()


def _style() -> str:
    return """
    <style>
      body { font-family: 'Noto Sans Bengali', 'Nirmala UI', sans-serif; line-height: 1.55; }
      h1 { color: #5B5FEF; font-size: 24px; margin-bottom: 4px; }
      h2 { color: #343A50; font-size: 18px; margin-top: 22px; }
      h3 { color: #4C5268; font-size: 15px; margin-top: 16px; }
      p, li { font-size: 14px; }
      table { border-collapse: collapse; width: 100%; margin: 8px 0; }
      th, td { border: 1px solid #C9D2E2; padding: 7px 9px; text-align: left; }
      th { background: #EEF1FF; color: #292D5E; }
      code { background: #EEF2F8; color: #34385C; padding: 2px 5px; }
      .note { background: #FFF5D9; border-left: 4px solid #F0A52B; padding: 10px; }
      .tip { background: #EAF8F2; border-left: 4px solid #35B982; padding: 10px; }
      a { color: #4F55DC; }
    </style>
    """

def _bengali_guide() -> str:
    return f"""
    {_style()}
    <h1>{escape(APP_DISPLAY_NAME)} — সহায়তা</h1>
    <p>বাংলা ও ইংরেজিতে Writing Pad অথবা অন্য Windows অ্যাপে কণ্ঠ দিয়ে লেখার পূর্ণ নির্দেশিকা।</p>

    <h2>দ্রুত শুরু</h2>
    <ol>
      <li>উপর থেকে <b>বাংলা · BN</b> অথবা <b>English · EN</b> নির্বাচন করুন।</li>
      <li><b>লেখার প্যাড</b> নির্বাচন করলে লেখা সফটওয়্যারের editor-এ আসবে।</li>
      <li><b>অন্য অ্যাপে লিখুন</b> নির্বাচন করলে Word, Notepad, browser ইত্যাদিতে cursor রাখুন।</li>
      <li><b>শুরু করুন</b> চাপুন অথবা <code>Ctrl+Shift+Space</code> ব্যবহার করুন।</li>
      <li>স্বাভাবিকভাবে বলুন; কাজ শেষে একই shortcut-এ microphone বন্ধ করুন।</li>
    </ol>

    <h2>Keyboard shortcut</h2>
    <table>
      <tr><th>কাজ</th><th>Shortcut</th></tr>
      <tr><td>ভয়েস টাইপিং শুরু/বন্ধ</td><td><code>Ctrl+Shift+Space</code></td></tr>
      <tr><td>Push-to-talk mode-এ ধরে কথা বলা</td><td><code>F9</code> ধরে রাখুন</td></tr>
      <tr><td>বাংলা voice language</td><td><code>Alt+Shift+B</code></td></tr>
      <tr><td>English voice language</td><td><code>Alt+Shift+E</code></td></tr>
      <tr><td>নতুন document</td><td><code>Ctrl+N</code></td></tr>
      <tr><td>ফাইল খুলুন / Save</td><td><code>Ctrl+O</code> / <code>Ctrl+S</code></td></tr>
      <tr><td>Undo / Redo</td><td><code>Ctrl+Z</code> / <code>Ctrl+Y</code></td></tr>
      <tr><td>খুঁজুন ও প্রতিস্থাপন</td><td><code>Ctrl+F</code></td></tr>
      <tr><td>Settings</td><td><code>Ctrl+,</code></td></tr>
    </table>

    <h2>ভয়েস কমান্ড</h2>
    <p>কমান্ডটি একটি সম্পূর্ণ আলাদা বাক্য হিসেবে বললে কাজ করবে।</p>
    <table>
      <tr><th>যা বলবেন</th><th>ফলাফল</th></tr>
      <tr><td>“নতুন লাইন” / “নতুন প্যারাগ্রাফ”</td><td>লাইন বা paragraph পরিবর্তন</td></tr>
      <tr><td>“শেষ শব্দ মুছুন”</td><td>আগের শব্দ মুছে দেয়</td></tr>
      <tr><td>“শেষ বাক্য মুছুন”</td><td>আগের বাক্য মুছে দেয়</td></tr>
      <tr><td>“সব মুছুন”</td><td>Writing Pad পরিষ্কার করার confirmation দেখায়</td></tr>
      <tr><td>“বাংলা মোড” / “ইংরেজি মোড”</td><td>Voice language পরিবর্তন</td></tr>
      <tr><td>“টাইপিং বন্ধ”</td><td>Microphone বন্ধ</td></tr>
      <tr><td>“কমা”, “দাঁড়ি”, “প্রশ্নবোধক চিহ্ন”</td><td>সংশ্লিষ্ট যতিচিহ্ন বসায়</td></tr>
    </table>

    <h2>Floating Bar ব্যবহার</h2>
    <ul>
      <li>Bar-টি ধরে screen-এর সুবিধাজনক স্থানে টেনে নিন; অবস্থান স্বয়ংক্রিয়ভাবে মনে থাকবে।</li>
      <li><b>PAD/GLOBAL</b> button দিয়ে লেখার গন্তব্য বদলান।</li>
      <li>Global mode-এ floating bar cursor focus নষ্ট না করেই কাজ করবে।</li>
      <li>“—” চাপলে bar লুকাবে; main window বা tray থেকে আবার দেখানো যাবে।</li>
    </ul>

    <h2>Save, Recovery ও Export</h2>
    <ul>
      <li>অসমাপ্ত লেখা auto-save হয় এবং crash/restart-এর পরে ফিরে আসে।</li>
      <li>TXT ও Markdown file খোলা/সেভ করা যায়।</li>
      <li>File menu থেকে Word (DOCX) অথবা PDF export করা যায়।</li>
      <li>সাম্প্রতিক file ও voice transcript Tools menu থেকে পাওয়া যাবে।</li>
    </ul>

    <h2>Online ও Offline Engine</h2>
    <ul>
      <li><b>Google (অনলাইন):</b> দ্রুত, কিন্তু internet প্রয়োজন এবং audio recognition service-এ পাঠানো হয়।</li>
      <li><b>Whisper (অফলাইন):</b> Audio কম্পিউটারেই process হয়। প্রথমবার নির্বাচিত model download হবে।</li>
      <li>Tiny দ্রুত; Base ভারসাম্যপূর্ণ; Small তুলনামূলক নির্ভুল কিন্তু ধীর ও বড়।</li>
    </ul>

    <h2>সমস্যা হলে</h2>
    <ul>
      <li>Microphone না চললে Settings থেকে সঠিক input device নির্বাচন করুন।</li>
      <li>কথা অস্পষ্ট হলে microphone কাছে রাখুন এবং background noise কমান।</li>
      <li>Global typing না হলে target app-এ cursor রেখে shortcut দিয়ে microphone চালু করুন।</li>
      <li>Administrator হিসেবে চলা app-এ লিখতে হলে এই সফটওয়্যারও একই privilege-এ চালাতে হবে।</li>
      <li>Google engine network error দিলে internet পরীক্ষা করুন অথবা Offline Whisper ব্যবহার করুন।</li>
    </ul>
    <p class="note"><b>গুরুত্বপূর্ণ:</b> অন্য অ্যাপে লেখার আগে সঠিক text field-এ cursor আছে কি না নিশ্চিত করুন। Password বা সংবেদনশীল field-এ অনিচ্ছাকৃতভাবে dictation চালাবেন না।</p>
    """


def _english_guide() -> str:
    return f"""
    {_style()}
    <h1>{escape(APP_DISPLAY_NAME)} — Help</h1>
    <p>Complete guide to Bengali and English dictation in the Writing Pad or another Windows application.</p>
    <h2>Quick start</h2>
    <ol>
      <li>Select <b>বাংলা · BN</b> or <b>English · EN</b>.</li>
      <li>Choose <b>Writing pad</b> for the internal editor or <b>Type in another app</b> for global typing.</li>
      <li>For global typing, place the cursor in Word, Notepad, a browser, or another text field.</li>
      <li>Press <b>Start</b> or <code>Ctrl+Shift+Space</code>, then speak normally.</li>
    </ol>
    <h2>Keyboard shortcuts</h2>
    <table>
      <tr><th>Action</th><th>Shortcut</th></tr>
      <tr><td>Start/stop dictation</td><td><code>Ctrl+Shift+Space</code></td></tr>
      <tr><td>Hold to talk when enabled</td><td><code>F9</code></td></tr>
      <tr><td>Bengali / English dictation</td><td><code>Alt+Shift+B</code> / <code>Alt+Shift+E</code></td></tr>
      <tr><td>New, open and save</td><td><code>Ctrl+N</code>, <code>Ctrl+O</code>, <code>Ctrl+S</code></td></tr>
      <tr><td>Undo / Redo</td><td><code>Ctrl+Z</code> / <code>Ctrl+Y</code></td></tr>
      <tr><td>Find/replace</td><td><code>Ctrl+F</code></td></tr>
      <tr><td>Settings</td><td><code>Ctrl+,</code></td></tr>
    </table>
    <h2>Voice commands</h2>
    <p>Speak a command as a complete standalone phrase: <b>new line</b>, <b>new paragraph</b>, <b>delete last word</b>, <b>delete last sentence</b>, <b>clear all</b>, <b>Bengali mode</b>, <b>English mode</b>, or <b>stop listening</b>. Punctuation includes comma, full stop, question mark and exclamation mark.</p>
    <h2>Floating bar and global typing</h2>
    <ul>
      <li>Drag the bar anywhere; its position is remembered.</li>
      <li>Use PAD/GLOBAL to change the text destination.</li>
      <li>The no-focus bar keeps the cursor in the target application.</li>
      <li>If the target application runs as Administrator, run this app at the same privilege level.</li>
    </ul>
    <h2>Files, recovery and speech engines</h2>
    <ul>
      <li>Auto-save restores unfinished writing after a restart.</li>
      <li>Open/save TXT and Markdown, or export DOCX and PDF.</li>
      <li>Google recognition needs internet. Whisper runs locally after its model has downloaded.</li>
      <li>Select a real input microphone in Settings if recording fails.</li>
    </ul>
    <p class="note"><b>Important:</b> Confirm the cursor is in the intended field before global dictation. Avoid dictating into password or sensitive fields accidentally.</p>
    """


def _bengali_developer() -> str:
    return f"""
    {_style()}
    <h1>{escape(DEVELOPER_NAME)}</h1>
    <h3>Flutter • Full Stack • Digital Solutions</h3>
    <p>পাঁচ বছরেরও বেশি অভিজ্ঞতাসম্পন্ন Flutter ও Full Stack developer। ইসলামিক, শিক্ষা ও ব্যবস্থাপনা-কেন্দ্রিক mobile app এবং web platform—ভাবনা থেকে বাস্তবায়ন পর্যন্ত পরিচ্ছন্ন, ব্যবহারবান্ধব ও নির্ভরযোগ্যভাবে তৈরি করেন।</p>
    <table>
      <tr><th>অভিজ্ঞতা</th><td>৫+ বছর</td></tr>
      <tr><th>সম্পন্ন প্রকল্প</th><td>২৩+</td></tr>
      <tr><th>মূল ফোকাস</th><td>ইসলামিক প্রযুক্তি, শিক্ষা ও management solution</td></tr>
      <tr><th>প্রযুক্তি</th><td>Flutter, Dart, Firebase, PHP, MySQL, REST API, Web Development, UI/UX</td></tr>
      <tr><th>শিক্ষা</th><td>হিফজুল কুরআন ও আলিম (এইচএসসি সমমান)</td></tr>
    </table>
    <p>প্রতিটি কাজে জটিল বিষয় সহজ করা, তথ্য সুন্দরভাবে সাজানো এবং দ্রুত ও স্বচ্ছ ব্যবহার-অভিজ্ঞতাকে অগ্রাধিকার দেন।</p>
    <h2>যোগাযোগ ও আরও তথ্য</h2>
    <ul>
      <li><a href="{PORTFOLIO_URL}">Portfolio website</a></li>
      <li><a href="mailto:hafezmahdihasan50@gmail.com">hafezmahdihasan50@gmail.com</a></li>
      <li><a href="tel:+8801790905350">০১৭৯০-৯০৫৩৫০</a></li>
      <li><a href="https://github.com/mdmahdihasan50">GitHub — mdmahdihasan50</a></li>
      <li><a href="https://facebook.com/hafezmahdihasan50">Facebook — hafezmahdihasan50</a></li>
    </ul>
    <p class="tip">মানুষের উপকারে প্রযুক্তি—যত্ন নিয়ে নির্মিত।</p>
    """


def _english_developer() -> str:
    return f"""
    {_style()}
    <h1>{escape(DEVELOPER_NAME)}</h1>
    <h3>Flutter • Full Stack • Digital Solutions</h3>
    <p>A Flutter and Full Stack developer with more than five years of experience, building clean and dependable mobile and web products for Islamic education, learning, and management.</p>
    <table>
      <tr><th>Experience</th><td>5+ years</td></tr>
      <tr><th>Completed projects</th><td>23+</td></tr>
      <tr><th>Focus</th><td>Islamic technology, education and management solutions</td></tr>
      <tr><th>Technology</th><td>Flutter, Dart, Firebase, PHP, MySQL, REST API, Web Development and UI/UX</td></tr>
      <tr><th>Education</th><td>Hifzul Quran and Alim (HSC equivalent)</td></tr>
    </table>
    <h2>Contact and portfolio</h2>
    <ul>
      <li><a href="{PORTFOLIO_URL}">Portfolio website</a></li>
      <li><a href="mailto:hafezmahdihasan50@gmail.com">hafezmahdihasan50@gmail.com</a></li>
      <li><a href="tel:+8801790905350">+880 1790-905350</a></li>
      <li><a href="https://github.com/mdmahdihasan50">GitHub — mdmahdihasan50</a></li>
      <li><a href="https://facebook.com/hafezmahdihasan50">Facebook — hafezmahdihasan50</a></li>
    </ul>
    <p class="tip">Technology built with care to serve people.</p>
    """
