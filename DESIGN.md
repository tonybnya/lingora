---
version: "alpha"
name: "Lumina AI - Intelligent Marketing Systems"
description: "Lumina Intelligent Dashboard Section is designed for demonstrating application workflows and interface hierarchy. Key features include clear information density, modular panels, and interface rhythm. It is suitable for product showcases, admin panels, and analytics experiences."
colors:
  primary: "#E85D22"
  secondary: "#FFFFFF"
  tertiary: "#F0F024"
  neutral: "#FFFFFF"
  background: "#FFFFFF"
  surface: "#E85D22"
  text-primary: "#FFFFFF"
  text-secondary: "#E85D22"
  border: "#FFFFFF"
  accent: "#E85D22"
typography:
  display-lg:
    fontFamily: "Inter"
    fontSize: "72px"
    fontWeight: 200
    lineHeight: "72px"
    letterSpacing: "-0.025em"
  body-md:
    fontFamily: "Inter"
    fontSize: "14px"
    fontWeight: 200
    lineHeight: "20px"
  label-md:
    fontFamily: "Inter"
    fontSize: "14px"
    fontWeight: 300
    lineHeight: "20px"
rounded:
  md: "0px"
spacing:
  base: "4px"
  sm: "4px"
  md: "8px"
  lg: "16px"
  xl: "24px"
  gap: "8px"
  card-padding: "32px"
  section-padding: "32px"
components:
  button-primary:
    backgroundColor: "#0A0A0A"
    textColor: "{colors.secondary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.md}"
    padding: "0px"
  button-link:
    textColor: "{colors.secondary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "0px"
---

## Overview

- **Composition cues:**
  - Layout: Grid
  - Content Width: Full Bleed
  - Framing: Glassy
  - Grid: Strong

## Colors

The color system uses dark mode with #E85D22 as the main accent and #FFFFFF as the neutral foundation.

- **Primary (#E85D22):** Main accent and emphasis color.
- **Secondary (#FFFFFF):** Supporting accent for secondary emphasis.
- **Tertiary (#F0F024):** Reserved accent for supporting contrast moments.
- **Neutral (#FFFFFF):** Neutral foundation for backgrounds, surfaces, and supporting chrome.

- **Usage:** Background: #FFFFFF; Surface: #E85D22; Text Primary: #FFFFFF; Text Secondary: #E85D22; Border: #FFFFFF; Accent: #E85D22

- **Gradients:** bg-gradient-to-r from-[#0A0A0A] to-[#0A0A0A]/20 via-[#0A0A0A]/70, bg-gradient-to-t from-[#0A0A0A] to-transparent via-[#0A0A0A]/50, bg-gradient-to-r from-transparent to-transparent via-white/10

## Typography

Typography relies on Inter across display, body, and utility text.

- **Display (`display-lg`):** Inter, 72px, weight 200, line-height 72px, letter-spacing -0.025em.
- **Body (`body-md`):** Inter, 14px, weight 200, line-height 20px.
- **Labels (`label-md`):** Inter, 14px, weight 300, line-height 20px.

## Layout

Layout follows a grid composition with reusable spacing tokens. Preserve the grid, full bleed structural frame before changing ornament or component styling. Use 4px as the base rhythm and let larger gaps step up from that cadence instead of introducing unrelated spacing values.

Treat the page as a grid / full bleed composition, and keep that framing stable when adding or remixing sections.

- **Layout type:** Grid
- **Content width:** Full Bleed
- **Base unit:** 4px
- **Scale:** 4px, 8px, 16px, 24px, 32px, 48px, 64px, 96px
- **Section padding:** 32px, 96px
- **Card padding:** 32px
- **Gaps:** 8px, 32px

## Elevation & Depth

Depth is communicated through glass, border contrast, and reusable shadow or blur treatments. Keep those recipes consistent across hero panels, cards, and controls so the page reads as one material system.

Surfaces should read as glass first, with borders, shadows, and blur only reinforcing that material choice.

- **Surface style:** Glass
- **Borders:** 1px #FFFFFF
- **Blur:** 12px, 24px

### Techniques
- **Gradient border shell:** Use a thin gradient border shell around the main card. Wrap the surface in an outer shell with 0px padding and a 0px radius. Drive the shell with linear-gradient(to right, rgb(10, 10, 10), rgba(10, 10, 10, 0.7), rgba(10, 10, 10, 0.2)) so the edge reads like premium depth instead of a flat stroke. Keep the actual stroke understated so the gradient shell remains the hero edge treatment. Inset the real content surface inside the wrapper with a slightly smaller radius so the gradient only appears as a hairline frame.

## Shapes

Shapes rely on a tight radius system anchored by 2px and scaled across cards, buttons, and supporting surfaces. Icon geometry should stay compatible with that soft-to-controlled silhouette.

Use the radius family intentionally: larger surfaces can open up, but controls and badges should stay within the same rounded DNA instead of inventing sharper or pill-only exceptions.

- **Corner radii:** 2px, 9999px
- **Icon treatment:** Linear
- **Icon sets:** Solar

## Components

Anchor interactions to the detected button styles.

### Buttons
- **Primary:** background #0A0A0A, text #FFFFFF, radius 0px, padding 0px, border 1px solid rgba(255, 255, 255, 0.1).
- **Links:** text #FFFFFF, radius 0px, padding 0px, border 0px solid rgb(229, 231, 235).

### Iconography
- **Treatment:** Linear.
- **Sets:** Solar.

## Do's and Don'ts

Use these constraints to keep future generations aligned with the current system instead of drifting into adjacent styles.

### Do
- Do use the primary palette as the main accent for emphasis and action states.
- Do keep spacing aligned to the detected 4px rhythm.
- Do reuse the Glass surface treatment consistently across cards and controls.
- Do keep corner radii within the detected 2px, 9999px family.

### Don't
- Don't introduce extra accent colors outside the core palette roles unless the page needs a new semantic state.
- Don't mix unrelated shadow or blur recipes that break the current depth system.
- Don't exceed the detected expressive motion intensity without a deliberate reason.

## Motion

Motion feels expressive but remains focused on interface, text, and layout transitions. Timing clusters around 150ms and 1000ms. Easing favors ease and cubic-bezier(0.4. Hover behavior focuses on color and stroke changes. Scroll choreography uses GSAP ScrollTrigger for section reveals and pacing.

**Motion Level:** expressive

**Durations:** 150ms, 1000ms, 300ms, 2000ms

**Easings:** ease, cubic-bezier(0.4, 0, 1), 0.2, 0.6

**Hover Patterns:** color, stroke, text

**Scroll Patterns:** gsap-scrolltrigger

## WebGL

Reconstruct the graphics as a full-bleed background field using webgl, renderer, alpha, antialias, dpr clamp, custom shaders. The effect should read as retro-futurist, technical, and meditative: dot-matrix particle field with green on black and sparse spacing. Build it from dot particles + soft depth fade so the effect reads clearly. Animate it as slow breathing pulse. Interaction can react to the pointer, but only as a subtle drift. Preserve dom fallback.

**Id:** webgl

**Label:** WebGL

**Stack:** ThreeJS, WebGL

**Insights:**
  - **Scene:**
    - **Value:** Full-bleed background field
  - **Effect:**
    - **Value:** Dot-matrix particle field
  - **Primitives:**
    - **Value:** Dot particles + soft depth fade
  - **Motion:**
    - **Value:** Slow breathing pulse
  - **Interaction:**
    - **Value:** Pointer-reactive drift
  - **Render:**
    - **Value:** WebGL, Renderer, alpha, antialias, DPR clamp, custom shaders

**Techniques:** Dot matrix, Breathing pulse, Pointer parallax, Shader gradients, DOM fallback

**Code Evidence:**
  - **HTML reference:**
    - **Language:** html
    - **Snippet:**
      ```html
      <!-- WebGL Background (Additive Wireframe) -->
      <canvas id="webgl-canvas" class="fixed top-0 left-0 w-screen h-screen z-[1] pointer-events-none mix-blend-screen opacity-50"></canvas>

      <!-- Structural Grid Overlay -->
      ```
  - **JS reference:**
    - **Language:** html
    - **Snippet:**
      ```html
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
      ```

## ThreeJS

Reconstruct the Three.js layer as a full-bleed background field with layered spatial depth that feels retro-futurist and technical. Use alpha, antialias, dpr clamp renderer settings, perspective, ~75deg fov, plane geometry, shadermaterial materials, and ambient + key + rim lighting. Motion should read as slow orbital drift, with poster frame + dom fallback.

**Id:** threejs

**Label:** ThreeJS

**Stack:** ThreeJS, WebGL

**Insights:**
  - **Scene:**
    - **Value:** Full-bleed background field with layered spatial depth
  - **Render:**
    - **Value:** alpha, antialias, DPR clamp
  - **Camera:**
    - **Value:** Perspective, ~75deg FOV
  - **Lighting:**
    - **Value:** ambient + key + rim
  - **Materials:**
    - **Value:** ShaderMaterial
  - **Geometry:**
    - **Value:** plane
  - **Motion:**
    - **Value:** Slow orbital drift

**Techniques:** Shader materials, Timeline beats, alpha, antialias, DPR clamp, Poster frame + DOM fallback

**Code Evidence:**
  - **HTML reference:**
    - **Language:** html
    - **Snippet:**
      ```html
      <!-- WebGL Background (Additive Wireframe) -->
      <canvas id="webgl-canvas" class="fixed top-0 left-0 w-screen h-screen z-[1] pointer-events-none mix-blend-screen opacity-50"></canvas>

      <!-- Structural Grid Overlay -->
      ```
  - **JS reference:**
    - **Language:** html
    - **Snippet:**
      ```html
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
      ```
