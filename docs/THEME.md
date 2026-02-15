# UI Theme Specification: "Modern Glass"

This document outlines the visual design system extracted from the reference image for the WireGuard UI customization phase.

## Visual Philosophy
The design follows a **Modern Glassmorphism** aesthetic, combining deep dark backgrounds with vibrant gradients and frosted-glass interface elements. It prioritizes clarity, high contrast for primary actions, and a premium "pro" feel.

## 1. Color Palette

### Background & Surface
| Element | Color Code | Description |
| :--- | :--- | :--- |
| **Main Background** | `Gradient` | Deep Navy (`#0A192F`) to Warm Amber (`#D48166`) |
| **Glass Panel** | `#1E2530` | 70% Opacity with 20px Backdrop Blur |
| **Panel Border** | `#3E444B` | 1px solid, subtle highlight |
| **Card Background** | `#262C36` | Slightly lighter than panel for depth |

### Accents & States
| Element | Color Code | Description |
| :--- | :--- | :--- |
| **Primary Action** | `#FF6B35` | Vibrant orange for "Confirm" buttons |
| **Success/Active** | `#00C853` | Emerald green for toggles and checkmarks |
| **Hover State** | `#FFFFFF10` | Subtle white overlay (10% opacity) |
| **Focus Border** | `#00C853` | Green ring for selected items |

## 2. Typography
- **Primary Font**: `Inter` or `Segoe UI Variable`
- **Header 1**: 20pt, Bold, White (`#FFFFFF`)
- **Body Text**: 14pt, Medium, Light Gray (`#E0E0E0`)
- **Secondary/Description**: 12pt, Regular, Muted Gray (`#9BA1A6`)

## 3. UI Components

### Glass Panels
- **Corner Radius**: `18px`
- **Shadow**: `0 8px 32px 0 rgba(0, 0, 0, 0.37)`
- **Border**: `1px solid rgba(255, 255, 255, 0.1)`

### Interactive List Items
- **Inactive**: Transparent background with bottom border (`#3E444B`).
- **Active/Selected**: Subtle gradient or solid `#2D3540` highlight.
- **Micro-interactions**: 200ms ease-in-out transition on hover.

### Buttons
- **Style**: Rounded (`12px`), heavy weight text.
- **Primary**: Orange background, white text.
- **Outline**: 1px border, transparent background, white text.

## 4. Layout & Spacing
- **Padding**: `24px` for main containers, `16px` for internal components.
- **Hierarchy**: Left-hand navigation with status indicators, centered main content area.
