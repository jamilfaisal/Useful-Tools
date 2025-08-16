def portions_needed(calories_per_cup, goal_calories, portion_ml=12.5):
    # 1 cup in ml
    ml_per_cup = 236.588

    # calories per ml
    calories_per_ml = calories_per_cup / ml_per_cup

    # calories per portion
    calories_per_portion = calories_per_ml * portion_ml

    # number of portions (rounded up to make sure cat gets at least the goal)
    portions = goal_calories / calories_per_portion

    return portions, calories_per_portion


if __name__ == "__main__":
    calories_per_cup = float(input("Enter calories per cup of food: "))
    goal_calories = float(input("Enter target calories for the cat: "))

    portions, cal_per_portion = portions_needed(calories_per_cup, goal_calories)

    print(f"\nCalories per dispenser portion: {cal_per_portion:.2f}")
    print(f"Portions needed to reach {goal_calories} kcal: {portions:.2f} (~{round(portions)} portions)")
