from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 485, 465
canvas = Image.new('RGBA', (W, H), (247, 234, 232, 255))

# We can create a high-res SVG or canvas rendering
# Let's test exact coordinates for the SVG:
svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 485 465" width="485" height="465">
  <defs>
    <!-- Drop shadow filter for badges -->
    <filter id="badgeShadow" x="-20%" y="-20%" width="150%" height="150%">
      <feDropShadow dx="0" dy="12" stdDeviation="15" flood-color="#000" flood-opacity="0.12"/>
    </filter>
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    
    <!-- Linear gradients -->
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#15B789"/>
      <stop offset="50%" stop-color="#12A27A"/>
      <stop offset="100%" stop-color="#0E8A66"/>
    </linearGradient>

    <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F97316"/>
      <stop offset="100%" stop-color="#D9531E"/>
    </linearGradient>
  </defs>

  <!-- 1. Radar Concentric Circles -->
  <g class="hero-radar-group" opacity="0.65">
    <circle cx="185" cy="195" r="62" fill="none" stroke="#E6BFB0" stroke-width="1.2" />
    <circle cx="185" cy="195" r="105" fill="none" stroke="#E6BFB0" stroke-width="1.2" />
    <circle cx="185" cy="195" r="150" fill="none" stroke="#E6BFB0" stroke-width="1.2" />
    <circle cx="185" cy="195" r="195" fill="none" stroke="#E6BFB0" stroke-width="1.2" />
  </g>

  <!-- 2. Orange Slanted Shape -->
  <!-- Peeks behind green badge on right: from x ~ 320 to 438, y ~ 222 to 375 -->
  <g class="hero-orange-shape" filter="url(#badgeShadow)">
    <path d="M 285 285 
             L 426 226 
             Q 438 221, 436 235 
             L 348 375 
             Q 343 383, 332 383 
             L 245 383 
             Z" 
          fill="url(#orangeGrad)" />
  </g>

  <!-- 3. Green Learn Badge -->
  <!-- Slanted rounded parallelogram -->
  <g class="hero-green-badge" filter="url(#badgeShadow)">
    <path d="M 185 195 
             L 260 160 
             L 422 144 
             Q 438 142, 432 156 
             L 325 320 
             Q 318 330, 305 330 
             L 170 330 
             Z" 
          fill="url(#greenGrad)" />
  </g>

  <!-- 4. Accent Dots -->
  <!-- Teal Dot -->
  <circle cx="255" cy="35" r="6" fill="#16B692" class="hero-dot-teal"/>
  <!-- Orange Dot -->
  <circle cx="71" cy="60" r="3.5" fill="#FC8B54" class="hero-dot-orange"/>
</svg>'''

with open('static/images/hero_shapes_backdrop.svg', 'w') as f:
    f.write(svg_content)

print('Saved static/images/hero_shapes_backdrop.svg')
