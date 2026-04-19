"""
╔══════════════════════════════════════════════════════════════╗
║        BALKAN EXPRESS — GAMSPy Optimization Model            ║
║   This script calculates the mathematically optimal route    ║
║   using the exact same data as the HTML game.                ║
╚══════════════════════════════════════════════════════════════╝

Installation:
    pip install gamspy

Execution:
    python balkan_optimizer.py
    python balkan_optimizer.py --budget 1200 --days 20 --style backpacker
    python balkan_optimizer.py --budget 850  --days 20 --style backpacker --compare
"""

import argparse
import sys

# ── Check if GAMSPy is installed ──
try:
    from gamspy import (
        Container, Set, Parameter, Variable,
        Equation, Model, Sense, Sum, Options
    )
    GAMSPY_OK = True
except ImportError:
    GAMSPY_OK = False


# ════════════════════════════════════════════════════════════════
# DATA — Identical to the HTML game (Translated from JS to Python)
# ════════════════════════════════════════════════════════════════

CITIES = [
    {
        "id": "sarajevo", "name": "Sarajevo", "country": "Bosnia and Herzegovina",
        "recommended_days": 3,
        "accommodations": [
            {"name": "Hostel Vagabond",    "cost": 12,  "xp": 95},
            {"name": "Hostel Kucha",       "cost": 8,   "xp": 80},
            {"name": "Balkan Han Hostel",  "cost": 14,  "xp": 100},
            {"name": "FG Boutique Hostel", "cost": 18,  "xp": 110},
            {"name": "Central Airbnb",     "cost": 35,  "xp": 110},
            {"name": "Hotel Europe",       "cost": 85,  "xp": 130},
        ],
        "activities": [
            {"name": "Bascarsija Walk",    "cost": 0,  "xp": 30},
            {"name": "Latin Bridge",       "cost": 0,  "xp": 25},
            {"name": "Tunnel of Hope",     "cost": 10, "xp": 50},
            {"name": "Trebevic Cable Car", "cost": 12, "xp": 60},
            {"name": "Yellow Fortress",    "cost": 0,  "xp": 45},
        ],
        "transport_cost": 0,   # Starting city
    },
    {
        "id": "belgrade", "name": "Belgrade", "country": "Serbia",
        "recommended_days": 3,
        "accommodations": [
            {"name": "Sun Hostel",             "cost": 7,   "xp": 80},
            {"name": "Up Hostel",              "cost": 10,  "xp": 92},
            {"name": "Good People Design",     "cost": 15,  "xp": 105},
            {"name": "Historic Airbnb",        "cost": 40,  "xp": 115},
            {"name": "Courtyard Marriott",     "cost": 90,  "xp": 130},
            {"name": "Hotel Moskva",           "cost": 110, "xp": 150},
        ],
        "activities": [
            {"name": "Kalemegdan Fortress",    "cost": 0,  "xp": 45},
            {"name": "Tesla Museum",           "cost": 8,  "xp": 60},
            {"name": "Zemun Walk",             "cost": 5,  "xp": 50},
            {"name": "Ada Ciganlija Bike",     "cost": 10, "xp": 55},
            {"name": "Skadarlija Music",       "cost": 15, "xp": 70},
        ],
        "transport_cost": 20,  # Average cost from Sarajevo
    },
    {
        "id": "kotor", "name": "Kotor", "country": "Montenegro",
        "recommended_days": 2,
        "accommodations": [
            {"name": "Pansion Kova",           "cost": 12,  "xp": 85},
            {"name": "Hostel Cent",            "cost": 15,  "xp": 90},
            {"name": "Old Town Hostel",        "cost": 19,  "xp": 98},
            {"name": "Scenic Airbnb",          "cost": 60,  "xp": 140},
            {"name": "Boutique Hotel Astoria", "cost": 110, "xp": 160},
            {"name": "Forza Mare",             "cost": 150, "xp": 180},
        ],
        "activities": [
            {"name": "Stari Grad Walk",        "cost": 0,  "xp": 35},
            {"name": "Fortress Climb",         "cost": 15, "xp": 75},
            {"name": "Perast & Lady of Rocks", "cost": 20, "xp": 65},
            {"name": "Bay Boat Tour",          "cost": 40, "xp": 90},
            {"name": "Blue Cave Tour",         "cost": 50, "xp": 95},
        ],
        "transport_cost": 25,
    },
    {
        "id": "budva", "name": "Budva", "country": "Montenegro",
        "recommended_days": 2,
        "accommodations": [
            {"name": "High Hostel",          "cost": 14,  "xp": 88},
            {"name": "Newborn Hostel",       "cost": 18,  "xp": 92},
            {"name": "Freedom Hostel",       "cost": 21,  "xp": 98},
            {"name": "Beachfront Airbnb",    "cost": 50,  "xp": 125},
            {"name": "Avala Resort",         "cost": 120, "xp": 160},
            {"name": "Splendid Resort",      "cost": 180, "xp": 200},
        ],
        "activities": [
            {"name": "Old Town Streets",     "cost": 0,  "xp": 35},
            {"name": "Mogren Beach",         "cost": 15, "xp": 55},
            {"name": "Sveti Stefan Tour",    "cost": 20, "xp": 65},
            {"name": "Canoe Rental",         "cost": 25, "xp": 50},
        ],
        "transport_cost": 10,  # Very close to Kotor
    },
    {
        "id": "tirana", "name": "Tirana", "country": "Albania",
        "recommended_days": 2,
        "accommodations": [
            {"name": "Tirana Backpacker",  "cost": 9,   "xp": 85},
            {"name": "Trip'n'Hostel",      "cost": 10,  "xp": 93},
            {"name": "Blue Door Hostel",   "cost": 14,  "xp": 98},
            {"name": "Modern Airbnb Bloku","cost": 30,  "xp": 105},
            {"name": "Rogner Hotel",       "cost": 90,  "xp": 140},
            {"name": "Maritim Plaza",      "cost": 130, "xp": 160},
        ],
        "activities": [
            {"name": "Pyramid Climb",      "cost": 0,  "xp": 30},
            {"name": "Bunk'Art 1 Bunker",  "cost": 7,  "xp": 65},
            {"name": "Dajti Cable Car",    "cost": 12, "xp": 55},
            {"name": "Blloku Nightlife",   "cost": 25, "xp": 60},
        ],
        "transport_cost": 23,
    },
    {
        "id": "skopje", "name": "Skopje", "country": "N. Macedonia",
        "recommended_days": 2,
        "accommodations": [
            {"name": "Shanti Hostel",    "cost": 8,   "xp": 85},
            {"name": "Get Inn Skopje",   "cost": 9,   "xp": 92},
            {"name": "Unity Hostel",     "cost": 12,  "xp": 95},
            {"name": "Central Airbnb",   "cost": 25,  "xp": 100},
            {"name": "Alexandar Hotel",  "cost": 90,  "xp": 130},
            {"name": "Skopje Marriott",  "cost": 140, "xp": 170},
        ],
        "activities": [
            {"name": "Old Bazaar Walk",  "cost": 0,  "xp": 45},
            {"name": "Millennium Cross", "cost": 8,  "xp": 55},
            {"name": "Matka Canyon",     "cost": 20, "xp": 85},
        ],
        "transport_cost": 22,
    },
    {
        "id": "pristina", "name": "Pristina", "country": "Kosovo",
        "recommended_days": 2,
        "accommodations": [
            {"name": "Buffalo Backpackers", "cost": 10,  "xp": 88},
            {"name": "Han Hostel",          "cost": 11,  "xp": 92},
            {"name": "Oda Hostel",          "cost": 12,  "xp": 96},
            {"name": "Luxury Airbnb",       "cost": 35,  "xp": 110},
            {"name": "Emerald Hotel",       "cost": 90,  "xp": 140},
            {"name": "Swiss Diamond",       "cost": 160, "xp": 220},
        ],
        "activities": [
            {"name": "NEWBORN Monument",    "cost": 0,  "xp": 20},
            {"name": "Ethnographic Museum", "cost": 3,  "xp": 35},
            {"name": "Bear Sanctuary",      "cost": 10, "xp": 65},
        ],
        "transport_cost": 12,
    },
]

FOOD_OPTIONS = {
    "backpacker": {"name": "Supermarket + Street", "daily_cost": 12, "xp": 5},
    "standard":   {"name": "Local Diner",          "daily_cost": 20, "xp": 15},
    "comfort":    {"name": "Restaurant",           "daily_cost": 35, "xp": 25},
}

RETURN_FLIGHTS = [
    {"name": "Pegasus",    "cost": 85,  "xp": 15},
    {"name": "SunExpress", "cost": 95,  "xp": 25},
    {"name": "Turkish Airlines", "cost": 185, "xp": 60},
]


# ════════════════════════════════════════════════════════════════
# HELPERS — Pretty Printing
# ════════════════════════════════════════════════════════════════

def draw_line(char="═", length=62):
    print(char * length)

def print_header(text, char="═"):
    draw_line(char)
    print(f"  {text}")
    draw_line(char)

# ════════════════════════════════════════════════════════════════
# GREEDY ALGORITHM (Fallback if GAMSPy is missing & for comparison)
# ════════════════════════════════════════════════════════════════

def solve_greedy(budget, total_days, style):
    food = FOOD_OPTIONS[style]
    remaining = budget
    day   = 0
    xp    = 0
    plan  = []

    for s in CITIES:
        if day >= total_days or remaining <= 0:
            break

        # Transport to city
        if remaining < s["transport_cost"]:
            continue
        remaining -= s["transport_cost"]

        # Best accommodation: xp/cost ratio
        affordable_acc = [a for a in s["accommodations"] if a["cost"] <= remaining * 0.4]
        if not affordable_acc:
            affordable_acc = [min(s["accommodations"], key=lambda a: a["cost"])]
        acc = max(affordable_acc, key=lambda a: a["xp"] / max(a["cost"], 1))

        # Days to spend in the city
        city_days = min(s["recommended_days"], total_days - day)

        # Activity selection: get top 3 highest xp/cost ratio
        act_budget = remaining * 0.3
        affordable_act = [a for a in s["activities"] if a["cost"] <= act_budget]
        affordable_act.sort(key=lambda a: a["xp"] / max(a["cost"], 0.1), reverse=True)
        selected_act = affordable_act[:3]

        daily_cost = (
            acc["cost"] * city_days
            + food["daily_cost"] * city_days
            + sum(a["cost"] for a in selected_act)
        )

        # If over budget, cut paid activities
        if daily_cost > remaining:
            daily_cost = acc["cost"] * city_days + food["daily_cost"] * city_days
            selected_act = [a for a in selected_act if a["cost"] == 0]

        remaining -= daily_cost
        day       += city_days
        city_xp = (
            acc["xp"] * city_days
            + food["xp"] * city_days
            + sum(a["xp"] for a in selected_act)
        )
        xp += city_xp

        plan.append({
            "city": s["name"], "country": s["country"],
            "days": city_days,
            "acc": acc["name"], "acc_cost": acc["cost"],
            "activities": [a["name"] for a in selected_act],
            "food": food["name"],
            "daily_cost": round(daily_cost),
            "city_xp": round(city_xp),
            "remaining": round(remaining),
        })

    # Return flight — cheapest possible
    flight = min(RETURN_FLIGHTS, key=lambda u: u["cost"])
    if remaining >= flight["cost"]:
        remaining -= flight["cost"]
        xp        += flight["xp"]
        return_flight = flight["name"]
    else:
        return_flight = "No budget left for flight"

    return {
        "method": "Greedy (XP/Cost Ratio)",
        "plan": plan,
        "total_xp": round(xp),
        "spent": round(budget - remaining),
        "remaining": round(remaining),
        "days": day,
        "return_flight": return_flight,
    }


# ════════════════════════════════════════════════════════════════
# GAMSPy MODEL — Mixed Integer Programming (MIP)
# ════════════════════════════════════════════════════════════════

def solve_gamspy(budget, total_days, style):
    food = FOOD_OPTIONS[style]
    flight = min(RETURN_FLIGHTS, key=lambda u: u["cost"])

    m = Container()

    # ── SETS ──
    S = Set(m, name="S", records=[s["id"] for s in CITIES], description="Cities")

    # Accommodation and activity sets: (city_id, index) pairs
    acc_records = []
    act_records = []
    for s in CITIES:
        for i, k in enumerate(s["accommodations"]):
            acc_records.append((s["id"], str(i)))
        for i, a in enumerate(s["activities"]):
            act_records.append((s["id"], str(i)))

    SK = Set(m, name="SK", domain=[S, "*"], records=acc_records, description="(City, Accommodation) pairs")
    SA = Set(m, name="SA", domain=[S, "*"], records=act_records, description="(City, Activity) pairs")

    # ── PARAMETERS ──
    transport_p = Parameter(m, name="transport", domain=[S],
        records=[(s["id"], s["transport_cost"]) for s in CITIES])
    days_p = Parameter(m, name="days", domain=[S],
        records=[(s["id"], s["recommended_days"]) for s in CITIES])

    acc_cost_p = Parameter(m, name="acc_cost", domain=[S, "*"],
        records=[(s["id"], str(i), k["cost"]) for s in CITIES for i, k in enumerate(s["accommodations"])])
    acc_xp_p = Parameter(m, name="acc_xp", domain=[S, "*"],
        records=[(s["id"], str(i), k["xp"]) for s in CITIES for i, k in enumerate(s["accommodations"])])

    act_cost_p = Parameter(m, name="act_cost", domain=[S, "*"],
        records=[(s["id"], str(i), a["cost"]) for s in CITIES for i, a in enumerate(s["activities"])])
    act_xp_p = Parameter(m, name="act_xp", domain=[S, "*"],
        records=[(s["id"], str(i), a["xp"]) for s in CITIES for i, a in enumerate(s["activities"])])

    # ── VARIABLES ──
    x = Variable(m, name="x", domain=[S],      type="binary", description="City selection")
    y = Variable(m, name="y", domain=[S, "*"], type="binary", description="Accommodation selection")
    z = Variable(m, name="z", domain=[S, "*"], type="binary", description="Activity selection")

    # ── OBJECTIVE FUNCTION ──
    total_xp = (
        Sum(SK, y[SK] * acc_xp_p[SK] * days_p[SK.domain[0]])
      + Sum(SA, z[SA] * act_xp_p[SA])
      + Sum(S,  x[S]  * food["xp"] * days_p[S])
    )
    obj = Equation(m, name="obj_eq", description="Objective: Maximize XP")

    # ── CONSTRAINTS ──
    budget_eq   = Equation(m, name="budget_eq", description="Budget constraint")
    days_eq     = Equation(m, name="days_eq",   description="Time constraint")
    acc_eq      = Equation(m, name="acc_eq",    domain=[S], description="Exactly 1 accommodation if city visited")
    act_eq      = Equation(m, name="act_eq",    domain=[S, "*"], description="No activity if city not visited")
    min_city_eq = Equation(m, name="min_city_eq", description="Min 3 cities visited")

    budget_eq[...] = (
        Sum(S,  x[S]  * transport_p[S])
      + Sum(SK, y[SK] * acc_cost_p[SK] * days_p[SK.domain[0]])
      + Sum(SA, z[SA] * act_cost_p[SA])
      + Sum(S,  x[S]  * food["daily_cost"] * days_p[S])
      + flight["cost"]
    ) <= budget

    days_eq[...]  = Sum(S, x[S] * days_p[S]) <= total_days
    acc_eq[S]     = Sum(SK.where[SK.domain[0] == S], y[SK]) == x[S]
    act_eq[SA]    = z[SA] <= x[SA.domain[0]]
    min_city_eq[...] = Sum(S, x[S]) >= 3

    model = Model(
        m, name="balkan_mip",
        equations=m.getEquations(),
        problem="MIP",
        sense=Sense.MAX,
        objective=total_xp,
    )

    model.solve(options=Options(time_limit=30))

    # ── PARSE RESULTS ──
    plan     = []
    final_xp = 0
    spent    = flight["cost"]

    x_vals = {r[0]: r[1] for r in x.records.values.tolist()} if x.records is not None else {}
    y_vals = {}
    z_vals = {}

    if y.records is not None:
        for row in y.records.values.tolist():
            y_vals[(row[0], row[1])] = row[2]
    if z.records is not None:
        for row in z.records.values.tolist():
            z_vals[(row[0], row[1])] = row[2]

    for s in CITIES:
        if x_vals.get(s["id"], 0) < 0.5:
            continue

        spent += s["transport_cost"]

        # Selected accommodation
        sec_acc = None
        for i, k in enumerate(s["accommodations"]):
            if y_vals.get((s["id"], str(i)), 0) > 0.5:
                sec_acc = k
                break
        if sec_acc is None:
            sec_acc = s["accommodations"][0]

        # Selected activities
        sec_act = []
        for i, a in enumerate(s["activities"]):
            if z_vals.get((s["id"], str(i)), 0) > 0.5:
                sec_act.append(a)

        day = s["recommended_days"]
        city_cost = (
            sec_acc["cost"] * day
            + food["daily_cost"] * day
            + sum(a["cost"] for a in sec_act)
        )
        city_xp = (
            sec_acc["xp"] * day
            + food["xp"] * day
            + sum(a["xp"] for a in sec_act)
        )
        spent += city_cost
        final_xp += city_xp

        plan.append({
            "city": s["name"], "country": s["country"],
            "days": day,
            "acc": sec_acc["name"], "acc_cost": sec_acc["cost"],
            "activities": [a["name"] for a in sec_act],
            "food": food["name"],
            "daily_cost": round(city_cost),
            "city_xp": round(city_xp),
            "remaining": round(budget - spent),
        })

    final_xp += flight["xp"]

    return {
        "method": "GAMSPy — Mixed Integer Programming (MIP)",
        "plan": plan,
        "total_xp": round(final_xp),
        "spent": round(spent),
        "remaining": round(budget - spent),
        "days": sum(p["days"] for p in plan),
        "return_flight": flight["name"],
    }


# ════════════════════════════════════════════════════════════════
# PRINT RESULTS
# ════════════════════════════════════════════════════════════════

def print_result(result):
    print_header(f"📊 {result['method']}", "─")
    for p in result["plan"]:
        print(f"\n  📍 {p['city']} ({p['country']}) — {p['days']} days")
        print(f"     🛏  {p['acc']}  ({p['acc_cost']}€/night)")
        print(f"     🍽  {p['food']}")
        if p["activities"]:
            print(f"     🎯  {' · '.join(p['activities'])}")
        print(f"     💸  Total: {p['daily_cost']}€  |  +{p['city_xp']} XP  |  Remaining: {p['remaining']}€")

    print()
    draw_line("─")
    print(f"  ✈️  Return Flight : {result['return_flight']}")
    print(f"  📅  Total Days    : {result['days']}")
    print(f"  ⭐  Total XP      : {result['total_xp']}")
    print(f"  💰  Amount Spent  : {result['spent']}€")
    print(f"  💚  Budget Left   : {result['remaining']}€")
    draw_line("─")


def print_comparison(gamspy_s, greedy_s, user_xp=None, user_spent=None):
    print_header("⚔️  COMPARISON — GAMSPy vs Greedy vs You")

    xp_diff = gamspy_s["total_xp"] - greedy_s["total_xp"]
    cost_diff = greedy_s["spent"] - gamspy_s["spent"]

    print(f"\n  {'':30} {'GAMSPy':>10} {'Greedy':>10}", end="")
    if user_xp is not None:
        print(f"  {'You':>8}", end="")
    print()

    draw_line("─")
    print(f"  {'Total XP':30} {gamspy_s['total_xp']:>10} {greedy_s['total_xp']:>10}", end="")
    if user_xp is not None:
        print(f"  {user_xp:>8}", end="")
    print()

    print(f"  {'Spent (€)':30} {gamspy_s['spent']:>10} {greedy_s['spent']:>10}", end="")
    if user_spent is not None:
        print(f"  {user_spent:>8}", end="")
    print()

    print(f"  {'Remaining (€)':30} {gamspy_s['remaining']:>10} {greedy_s['remaining']:>10}", end="")
    if user_xp is not None:
        print(f"  {'—':>8}", end="")
    print()

    print(f"  {'Cities Visited':30} {len(gamspy_s['plan']):>10} {len(greedy_s['plan']):>10}")
    draw_line("─")

    print(f"\n  📈 GAMSPy scored {xp_diff:+} XP better than greedy")
    print(f"  💰 GAMSPy is {cost_diff:+}€ {'cheaper' if cost_diff>0 else 'more expensive'} than greedy")

    if user_xp is not None:
        u_diff = gamspy_s["total_xp"] - user_xp
        print(f"  🎮 GAMSPy collected {u_diff:+} XP {'more' if u_diff>0 else 'less'} than you did")

    draw_line()
    if xp_diff > 0:
        print("  ✅ MIP solver found combinations the greedy approach missed.")
    else:
        print("  ℹ️  The greedy approach worked well enough for this dataset.")
    draw_line()


# ════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Balkan Express — GAMSPy Optimization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python balkan_optimizer.py
  python balkan_optimizer.py --budget 850 --days 20 --style backpacker
  python balkan_optimizer.py --budget 1500 --days 25 --style standard --compare
  python balkan_optimizer.py --greedy-only
        """
    )
    parser.add_argument("--budget",      type=float, default=1000, help="Total budget in € (default: 1000)")
    parser.add_argument("--days",        type=int,   default=20,   help="Total holiday days (default: 20)")
    parser.add_argument("--style",       choices=["backpacker", "standard", "comfort"],
                                         default="backpacker", help="Travel style")
    parser.add_argument("--compare",     action="store_true", help="Compare GAMSPy vs Greedy")
    parser.add_argument("--greedy-only", action="store_true", help="Run only the greedy algorithm without GAMSPy")
    parser.add_argument("--user-xp",     type=int, help="The XP you earned in the game (for comparison)")
    parser.add_argument("--user-spent",  type=int, help="The amount you spent in the game (for comparison)")

    args = parser.parse_args()

    print()
    print_header("🎒 BALKAN EXPRESS — Optimization Engine", "╔")
    print(f"  Budget: {args.budget}€  |  Duration: {args.days} days  |  Style: {args.style}")
    draw_line()
    print()

    # ── GREEDY ──
    greedy_result = solve_greedy(args.budget, args.days, args.style)
    print_result(greedy_result)
    print()

    if args.greedy_only:
        return

    # ── GAMSPy ──
    if not GAMSPY_OK:
        print("  ⚠️  GAMSPy is not installed!")
        print("  Install it using: pip install gamspy\n")
        print("  Greedy result shown above.")
        print("  Install GAMSPy for full MIP optimization.")
        return

    print("  🔄 GAMSPy MIP Solver is starting...\n")
    try:
        gamspy_result = solve_gamspy(args.budget, args.days, args.style)
        print_result(gamspy_result)
        print()

        if args.compare or args.user_xp:
            print_comparison(
                gamspy_result, greedy_result,
                args.user_xp, args.user_spent
            )

    except Exception as e:
        print(f"  ❌ GAMSPy Error: {e}\n")
        print("  Continuing with Greedy result.")
        if args.compare:
            print("\n  (Both solutions are required for comparison)")

if __name__ == "__main__":
    main()