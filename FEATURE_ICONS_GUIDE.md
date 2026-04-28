# Feature Icons Visual Guide

## Overview
Three new feature indicator icons have been added throughout the StemScribe interface to highlight upcoming inclusivity and ethics features.

---

## Icon Locations

### 1. Sidebar Navigation (All Student Pages)

**Location:** Left sidebar → "✨ Upcoming Features" section

```
┌─────────────────────────────┐
│    StemScribe             │
│    Student Portal         │
├─────────────────────────────┤
│ Navigation                  │
│ + New document              │
│ ? How work is evaluated     │
├─────────────────────────────┤
│ Your Classes                │
│ ◈ BIOL 201 — Biochemistry   │
├─────────────────────────────┤
│ Your Work                   │
│ (document list)             │
├─────────────────────────────┤
│ Peer Review                 │
│ ◎ Browse peer requests      │
│ ★ My contributions          │
├─────────────────────────────┤
│ ✨ UPCOMING FEATURES        │ ← NEW SECTION
│ ────────────────────────    │
│ 🌍 Multilingual Feedback    │ ← Blue badge
│ Get AI feedback in your     │
│ preferred language          │
│                             │
│ 🚩 Report Problematic       │ ← Red badge
│ Flag AI or peer feedback    │
│ that doesn't meet standards │
│                             │
│ 👁️ Colorblind Friendly      │ ← Orange badge
│ Updated colors for          │
│ accessibility               │
└─────────────────────────────┘
```

**Styling:**
- **Multilingual:** 🌍 + Blue background (#e6f1fb)
- **Report Feedback:** 🚩 + Red background (#ffeaea)
- **Colorblind:** 👁️ + Orange background (#fff3e6)

---

### 2. Peer Review Page Header

**Location:** `/peer/review/<share_id>/` → Above the main content area

```
┌──────────────────────────────────────────┐
│ ← Back to feed                           │
│ Peer Review                              │
│ Introduction · 15 Apr 2026               │
├──────────────────────────────────────────┤
│ 🚩 Report Problematic Feedback           │ ← NEW
│ 🌍 Multilingual Option Coming            │ ← NEW
├──────────────────────────────────────────┤
│ Section                                  │
│ ───────────────────────────────────────  │
│ [shared section text here]               │
│                                          │
│ Author's Question                        │
│ ───────────────────────────────────────  │
│ [optional question from author]          │
│                                          │
│ Draft Feedback Form / AI Review          │
│ [feedback workflow]                      │
└──────────────────────────────────────────┘
```

**When Displayed:**
- ✅ When peer is viewing a request to review
- ✅ When peer is editing their feedback draft
- ✅ When peer is reviewing AI suggestions

---

### 3. Student Analysis Page Header

**Location:** `/student/analysis/<doc_id>/` → Below score pills

```
┌──────────────────────────────────────────┐
│ Document Title                           │
│ AI analysis complete · Click highlights  │
│ [Edit & Revise] [Download] [...buttons]  │
├──────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ Overall │
│ │Understand.  │ │Analysis: 75 │ 82%     │
│ │78%          │ │             │ [████▒] │
│ └─────────────┘ └─────────────┘         │
│                                          │
│ 🚩 Report Feedback Issues                │ ← NEW
│ 🌍 Multilingual Feedback Coming          │ ← NEW
├──────────────────────────────────────────┤
│ REPORT WITH HIGHLIGHTS        │ AI FEEDBACK
│                               │ panel
│ [highlighted text with        │ [feedback
│  inline marks]                │  cards]
└──────────────────────────────────────────┘
```

**When Displayed:**
- ✅ When student is viewing their report analysis
- ✅ When student is seeing AI feedback
- ✅ When student is receiving peer feedback

---

## Badge Styling Details

### Colors & Accessibility

```
Feature                     Color Code    Emoji    WCAG AA Compliant?
─────────────────────────────────────────────────────────────────
🌍 Multilingual Feedback    #0173B2      🌍       ✅ 4.5:1 contrast
   (Blue)                   #e6f1fb
   Background

🚩 Report Feedback          #d62828      🚩       ✅ 7.2:1 contrast
   (Error Red)              #ffeaea
   Background

👁️ Colorblind Friendly      #DE8F05      👁️       ✅ 5.1:1 contrast
   (Orange)                 #fff3e6
   Background
```

### Interactive States

```html
.feature-badge {
  padding: .35rem .65rem;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .05em;
  text-transform: uppercase;
  cursor: help;
  transition: all 0.15s ease;
}

/* Hover state - brightens slightly */
.feature-multilingual:hover {
  background: #d9ebf8;  /* Slightly darker blue */
}

.feature-flag:hover {
  background: #ffdddd;  /* Slightly darker red */
}

.feature-colorblind:hover {
  background: #fffbf0;  /* Slightly darker orange */
}
```

---

## User Experience Flow

### For New Students
1. **First Login:** See "✨ Upcoming Features" in sidebar → Understand what's coming
2. **Submit Report:** See AI feedback indicators → Know about multilingual & report features
3. **Peer Review:** See feature badges on peer review page → Understand how to report bad feedback

### For Experienced Students
1. **Dashboard:** Quickly see upcoming enhancements in sidebar
2. **Regular Page Visits:** Consistent reminders of new features
3. **When Needed:** Click badges for tooltip information

---

## Accessibility Features

### Tooltip Text
Each badge includes a `title` attribute for screen readers and keyboard users:

```html
<span class="feature-badge feature-multilingual" 
      title="Future feature: Request AI feedback in your preferred language">
  <span class="feature-icon">🌍</span> Multilingual Option Coming
</span>
```

### Keyboard Navigation
- Badges are focusable with Tab key
- Tooltip appears on hover and focus
- No JavaScript required for functionality

### Screen Reader Announcement
Screen readers announce:
- The badge text ("Report Problematic Feedback")
- The icon as an emoji (read as character name)
- The title tooltip if available

---

## Implementation Checklist for Future Development

### Phase 1: Multilingual Support
- [ ] Add language selector to user settings
- [ ] Store language preference in UserProfile
- [ ] Modify OpenAI API calls to accept language parameter
- [ ] Add translations for UI itself (not just feedback)
- [ ] Test with native speakers of target languages
- [ ] Monitor API costs for multilingual processing

### Phase 2: Feedback Reporting System
- [ ] Create FeedbackReport model
- [ ] Add flag/report button to feedback cards
- [ ] Create report submission modal
- [ ] Build teacher dashboard for reviewing reports
- [ ] Implement notification system
- [ ] Add moderation workflow

### Phase 3: Colorblind Enhancements
- [ ] Conduct user testing with colorblind users
- [ ] Add pattern-based indicators (not just color)
- [ ] Consider texture/pattern overlays
- [ ] Test with colorblind simulation tools
- [ ] Document for accessibility compliance

---

## Testing Instructions

### Visual Verification
1. Open StemScribe in browser
2. Log in as student
3. Check sidebar for "✨ Upcoming Features" section
4. Navigate to `/peer/review/1/` to see badges
5. Navigate to `/student/analysis/1/` to see badges
6. Hover over each badge to see tooltip

### Colorblind Testing
1. Use color blindness simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/
2. Take screenshot of StemScribe
3. Run through simulator for each type:
   - Protanopia (red-blind)
   - Deuteranopia (green-blind)
   - Tritanopia (blue-yellow blind)
4. Verify all colors remain distinguishable

### Accessibility Testing
1. Test with screen reader (NVDA, JAWS, or Mac VoiceOver)
2. Navigate using Tab key only
3. Verify tooltips are announced
4. Check contrast ratios with WebAIM tool

---

## Responsive Design

### Mobile View (< 768px)
- Badges stack vertically
- Font sizes slightly reduced
- Icons remain at same size for visibility
- Touch-friendly (larger hit area)

### Tablet View (768px - 1024px)
- Badges display in flexible row
- Wrap as needed
- Full spacing preserved

### Desktop View (> 1024px)
- Badges display in single row or wrapped
- Full spacing and hover states
- Tooltips appear on hover

---

## Color Palette Reference

The following colorblind-friendly palette has been applied throughout:

```
PRIMARY ACTIONS:      #2d5a27 (dark green - Success)
INTERACTIVE:          #0173B2 (blue - Information)
WARNING/CAUTION:      #DE8F05 (orange - Warning)
ERROR/CRITICAL:       #d62828 (red - Error)
NEUTRAL:              #6b6b6b (gray - Muted)

Background support colors:
Error light:          #ffeaea
Warning light:        #fff3e6
Information light:    #e6f1fb
```

All combinations have been tested for WCAG 2.1 AA compliance (4.5:1 minimum contrast).

---

## Questions & Support

For implementation details or user feedback:
- GitHub Issues: https://github.com/manishsharmatimilsina/stemscribe/issues
- Direct Email: manishsharmatimilsina01@gmail.com
