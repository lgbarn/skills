---
name: recipe-creator
description: Create original recipes from scratch with expertise in world cuisines, African American Southern soul food, flavor pairing science, baking science, cooking chemistry, and beverage pairing. Use whenever someone mentions food, cooking, recipes, meals, dishes, ingredients, baking, grilling, meal prep, drinks, cocktails, or what to drink with dinner. Also use when someone asks "what should I make for dinner", "I have these ingredients", "what goes well with X", "meal ideas", "what pairs with", "what should I drink with this", "make me a cocktail", "create a drink", or describes available ingredients and wants suggestions. Triggers on any food-related request including dietary adaptations, cuisine exploration, flavor pairing questions, baking troubleshooting, drink creation, beverage pairing, or "help me cook something". Even casual mentions like "I'm hungry" or "dinner tonight" with any cooking context should activate this skill.
---

# Recipe Creator

Create original recipes from scratch, grounded in culinary science and world cuisine traditions.
Special expertise in African American Southern / soul food cuisine.

---

## When to Use This Skill

**Use for:**
- Creating a new recipe from scratch
- Exploring what flavors or ingredients pair well together
- Adapting recipes for dietary restrictions (vegan, gluten-free, dairy-free, etc.)
- Exploring a specific cuisine tradition
- Understanding WHY certain flavor combinations work
- Suggesting ingredient substitutions that respect cultural authenticity
- Planning meals around available ingredients
- Developing fusion or experimental dishes grounded in science

**Do NOT use for:**
- Medical nutrition advice or therapeutic diets
- Precise calorie counting or macro tracking
- Food safety certification or HACCP planning
- Restaurant recommendations

---

## Recipe Creation Workflow

### Step 1: Understand the Request

Consider these dimensions:
- What cuisine or tradition?
- What ingredients are available or desired?
- Any dietary restrictions? (vegan, halal, gluten-free, nut allergy, etc.)
- Serving size and occasion? (weeknight, entertaining, comfort food, holiday)
- Skill level? (beginner, intermediate, advanced)
- What equipment is available? (assume standard home kitchen unless stated otherwise)

**When to ask vs. when to infer:** If the request is specific enough to build a recipe ("give me a soul food collard greens recipe for 4"), go straight to cooking. If it's open-ended ("make me a chicken recipe"), ask 1-2 clarifying questions — focus on the most impactful unknowns (cuisine direction and dietary needs matter most; serving size and skill level can be assumed). Don't interrogate — a short "Any cuisine preference or dietary needs I should know about?" covers it.

### Step 2: Select Cuisine Foundation
- Identify the cuisine's aromatic base (mirepoix, sofrito, trinity, etc.)
- Determine the foundational fat and cooking method
- Reference [cuisines.md](cuisines.md) for detailed profiles
- For soul food, reference [soul-food.md](soul-food.md)

### Step 3: Choose Flavor Profile
- Apply flavor pairing principles (see [flavor-science.md](flavor-science.md))
- Balance the 5 basic tastes: sweet, salty, sour, bitter, umami
- Consider aromatic layering: base notes, middle notes, top notes
- Add texture contrast and temperature interplay

### Step 4: Build Ingredient List
- Select primary protein or base ingredient
- Choose aromatic foundation appropriate to the cuisine
- Layer seasonings and spices
- Include acid, fat, and finishing elements
- Group ingredients by recipe component

### Step 5: Develop Technique Sequence
- Select cooking techniques matched to ingredients and desired outcome
- Reference [techniques.md](techniques.md) for method details
- Sequence steps for efficiency (what can happen in parallel)
- Include sensory cues at each stage
- Stick to standard home kitchen equipment (oven, stovetop, sheet pans, pots, skillets) unless the user mentions specific tools. If a recipe genuinely needs something less common (cast iron, Dutch oven, food processor), note it upfront and suggest alternatives

### Step 6: Write Complete Recipe
- Follow the Standard Recipe Output Format below
- Include "Why This Works" flavor science notes
- Provide substitutions for common restrictions
- Add make-ahead and storage guidance

### Step 7: Suggest Beverage Pairing
- Include at least one drink pairing with every recipe
- Offer both alcoholic and non-alcoholic options
- For special occasions or when asked, create a custom drink to accompany the dish
- Reference [beverage-pairing.md](beverage-pairing.md) for pairing science and custom drink creation

---

## Standard Recipe Output Format

```
### [RECIPE NAME]
*[One-sentence evocative description]*

**Cuisine**: [tradition and region]
**Story**: [1-2 sentences on cultural origin or inspiration]
**Servings**: [number]
**Prep Time**: [minutes]
**Cook Time**: [minutes]
**Total Time**: [minutes]
**Difficulty**: [Beginner / Intermediate / Advanced]

#### Ingredients

**For the [component name]:**
- [amount] [unit] [ingredient], [prep instruction]
- [amount] [unit] [ingredient], [prep instruction]

**For the [second component]:**
- [amount] [unit] [ingredient], [prep instruction]

#### Instructions

1. **[Phase name]**: [Detailed instruction with sensory cues —
   what it looks like, sounds like, smells like when done]
2. **[Phase name]**: [Next step with timing AND visual/tactile cues]
3. ...

#### Why This Works
[2-3 sentences explaining the flavor science: what compounds interact,
why the technique matters, what the cultural context is]

#### Variations & Substitutions

| Original | Substitute | Notes |
|----------|-----------|-------|
| [ingredient] | [alternative] | [impact on flavor/texture] |

#### Pairs With
- **Wine/Beer**: [specific recommendation with why]
- **Cocktail**: [a cocktail that complements the dish, with brief recipe]
- **Non-alcoholic**: [a non-alcoholic option — tea, agua fresca, lemonade, shrub, etc.]

#### Cook's Notes
- **Make ahead**: [what can be prepped in advance]
- **Storage**: [how to store, how long it keeps]
- **Scaling**: [notes on doubling/halving]
```

**Key format principles:**
- Sensory cues over timers: "until translucent and fragrant" not just "5 minutes"
- Group ingredients by component for complex dishes
- Always include substitutions, noting impact on authenticity

**"Why This Works" is the differentiator** — this is what separates a great recipe from a list of steps. Go beyond "the acid brightens the dish" into *which* compounds interact and *why* the technique produces the result. Name the reactions (Maillard, caramelization, denaturation) and connect them to what the cook will taste.

Good: "The buttermilk's lactic acid denatures surface proteins, tenderizing the meat while its sugars participate in Maillard browning with the flour — producing pyrazines and furanones that create that complex, savory crust."

Weak: "The buttermilk tenderizes the chicken and helps the coating brown."

**Scaling guidance:** Doubling a braise or soup is mostly linear — just use a bigger pot. But baking is chemistry: leavening agents (baking powder, yeast) don't scale linearly past 2x, fats can over-tenderize at high ratios, and oven time changes non-linearly with mass. When scaling baked goods past 2x, note that the user should increase leavening by only 1.5x per doubling and add 10-15% more baking time. For fried foods, batch size stays the same — scale by frying more batches, not bigger batches.

---

## Core Flavor Principles

### The 5 Basic Tastes (+ Fat)

| Taste | Sources | Role in Balance |
|-------|---------|-----------------|
| **Sweet** | Sugar, honey, caramelized onions, sweet potatoes, fruits | Rounds harsh edges, balances acid and heat |
| **Salty** | Salt, soy sauce, fish sauce, miso, cured meats | Amplifies all other flavors, suppresses bitterness |
| **Sour** | Vinegar, citrus, tomatoes, fermented foods, wine | Brightens, cuts richness, adds liveliness |
| **Bitter** | Dark greens, coffee, dark chocolate, charred surfaces | Adds complexity, prevents cloying sweetness |
| **Umami** | Parmesan, mushrooms, soy sauce, tomato paste, smoked meats | Deep savory satisfaction, makes dishes feel "complete" |
| **Fat** | Butter, oil, cream, nuts, avocado | Carries flavor, adds richness, creates mouthfeel |

### Pairing Approaches

| Approach | Principle | Example |
|----------|-----------|---------|
| **Complementary** | Shared aroma compounds create harmony | Tomato + basil (shared linalool) |
| **Contrasting** | Opposing elements create exciting balance | Sweet + spicy, rich + acidic |
| **Bridging** | Third ingredient connects two unlike items | Mushroom bridges beef and soy sauce (shared umami) |

For molecular compound families, scientific pairings, and the full pairing decision tree, see [flavor-science.md](flavor-science.md).

---

## Soul Food & Southern Cuisine

The skill's area of deepest expertise. African American Southern cuisine — soul food — is a tradition born from West African culinary knowledge transformed through the experience of slavery in the American South.

**Signature elements:**
- **The Trinity**: onion, celery, green bell pepper (aromatic base)
- **Smoke as seasoning**: ham hocks, smoked turkey, bacon drippings
- **Core spices**: garlic powder, onion powder, smoked paprika, cayenne, black pepper
- **Techniques**: slow-braising greens, deep-frying in cast iron, baking custard-set mac & cheese
- **Key ingredients**: collard greens, cornmeal, okra, black-eyed peas, sweet potatoes, buttermilk

**Classic dishes**: fried chicken, collard greens, cornbread (no sugar), baked mac & cheese, candied yams, gumbo, red beans & rice, peach cobbler, banana pudding, catfish, oxtails, hoppin' John, sweet potato pie

For the complete deep dive — history, regional variations, classic dish breakdowns, and vegan soul food adaptations — see [soul-food.md](soul-food.md).

---

## World Cuisine Quick Reference

| Cuisine | Signature Flavors | Key Ingredients | Core Technique |
|---------|------------------|-----------------|----------------|
| **West African** | Bold, earthy, spicy-sweet | Palm oil, scotch bonnets, peanuts | Slow frying in palm oil, pounding |
| **Ethiopian** | Warm, complex, aromatic | Berbere, niter kibbeh, teff | Spice blending, injera fermentation |
| **North African** | Warm spice, citrus, floral | Ras el hanout, preserved lemons, harissa | Tagine slow-cooking |
| **Caribbean** | Tropical, aromatic heat | Allspice, scotch bonnets, coconut | Jerk smoking, curry braising |
| **Mexican** | Earthy, bright, layered heat | Dried chilies, cumin, lime, corn masa | Chile toasting, mole building |
| **French** | Classical, technique-driven | Butter, wine, herbs de Provence | Mother sauces, reduction |
| **Italian** | Bold aromatics, herbaceous | Tomatoes, olive oil, garlic, basil | Soffritto base, pasta craft |
| **Indian** | Complex layered spice | Garam masala, turmeric, yogurt | Tempering (tadka), spice layering |
| **Thai** | Sweet-sour-salty-spicy balance | Lemongrass, fish sauce, coconut milk | Mortar-and-pestle curry paste |
| **Chinese** | Wok hei, balanced flavors | Five-spice, soy sauce, ginger | High-heat wok, regional styles |
| **Japanese** | Clean umami, minimalist | Dashi, miso, soy, mirin | Dashi extraction, knife precision |
| **Korean** | Fermented, spicy, balanced | Gochugaru, doenjang, sesame | Fermentation, banchan balance |
| **Middle Eastern** | Warm, tangy, aromatic | Sumac, za'atar, tahini, pomegranate | Grilling, flatbread, mezze |
| **Bosnian** | Hearty, smoky, onion-rich | Kajmak, phyllo, veal, paprika | Sac roasting, charcoal grilling |
| **Guyanese** | Curry-spiced, tropical, cassareep depth | Green seasoning, cassareep, wiri wiri | Curry burning, one-pot cooking |
| **Brazilian** | Tropical, smoky, African-rooted | Dende oil, black beans, farofa | Churrasco, Bahian stewing |

For full profiles with signature dishes, essential pantry, and cuisine affinities, see [cuisines.md](cuisines.md).

---

## Dietary Adaptations

When adapting recipes for dietary needs, follow these principles:

1. **Respect the dish's soul**: Preserve the essential character and flavor profile
2. **Match the function**: Replace based on what the ingredient DOES (binding, fat, acid, umami)
3. **Acknowledge trade-offs**: Be honest when a substitution changes the dish significantly
4. **Cultural sensitivity**: Note when an adaptation moves away from traditional preparation

### Common Substitution Strategies

| Restriction | Strategy | Example |
|-------------|----------|---------|
| **Vegan** | Replace umami with mushroom/miso/nutritional yeast | Smoked mushrooms for ham hock in greens |
| **Gluten-free** | Rice flour, cornmeal, nut flours | Cornmeal crust instead of wheat flour breading |
| **Dairy-free** | Coconut cream, oat cream, cashew cream | Coconut cream in mac and cheese sauce |
| **Low-sodium** | Build flavor through acid, spice, and smoke | Smoked paprika + lemon for depth without salt |
| **Nut allergy** | Seed butters (sunflower, tahini) | Sunflower butter for peanut-based sauces |
| **Egg-free** | Flax eggs, aquafaba, silken tofu | Aquafaba meringue for banana pudding |
| **Halal/Kosher** | Substitute pork with smoked turkey, beef | Turkey wings for ham hocks, beef bacon |

---

## Supporting Files

| File | Content | Load When |
|------|---------|-----------|
| [soul-food.md](soul-food.md) | African American Southern cuisine deep dive | User asks about soul food, Southern cooking |
| [bosnian-cuisine.md](bosnian-cuisine.md) | Bosnian cuisine deep dive | User asks about Bosnian, Balkan, or Ottoman-influenced cooking |
| [guyanese-cuisine.md](guyanese-cuisine.md) | Guyanese cuisine deep dive | User asks about Guyanese, Guyana, or Indo-Caribbean cooking |
| [cuisines.md](cuisines.md) | 14 world cuisine profiles | User asks about a specific cuisine |
| [flavor-science.md](flavor-science.md) | Molecular pairing and flavor compound science | User asks WHY pairings work |
| [techniques.md](techniques.md) | Cooking methods with cuisine context | User needs technique guidance |
| [baking-science.md](baking-science.md) | Flour, leavening, fat, sugar, eggs — the chemistry of baking | User asks about baking, bread, pastry, cakes, cookies, pies |
| [cooking-science.md](cooking-science.md) | Protein denaturation, collagen, starch, emulsions, pH, osmosis | User asks WHY a technique works, troubleshooting cooking failures |
| [beverage-pairing.md](beverage-pairing.md) | Wine, beer, cocktail, and non-alcoholic pairing + custom drink creation | User wants a drink suggestion, pairing advice, or custom beverage recipe |
