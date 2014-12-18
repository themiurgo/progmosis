import progmosis

user_a = [(0, "A"), (2, "B"), (4, "A")]
user_b = [(0, "A"), (4, "A")]
user_c = [(0, "A"), (1, "B"), (2, "A"), (4, "A")]
user_d = [(0, "A"), (1, "B"), (2, "A"), (4, "A")]
user_e = [(0, "A"), (1, "B"), (3, "C"), (4, "A")]
user_f = [(0, "A"), (1, "B"), (2, "C"), (3, "A"), (4, "D"), (5, "A")]
user_g = [(0, "A"), (1, "B"), (2, "C"), (3, "D"), (4, "E"), (5, "A")]

f_infected = {
    'A': 1, 
    'B': 0, 
    'C': 1,
    'D': 0,
    'E': 0,
}

print progmosis.evaluate_risk(user_a, f_infected, 1)
print progmosis.evaluate_risk(user_b, f_infected, 1)
print progmosis.evaluate_risk(user_c, f_infected, 1)
print progmosis.evaluate_risk(user_d, f_infected, 1)
print progmosis.evaluate_risk(user_e, f_infected, 1)
print progmosis.evaluate_risk(user_f, f_infected, 1)
print progmosis.evaluate_risk(user_g, f_infected, 1)
