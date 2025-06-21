import clips


class LogisticsExpertSystem:
    def __init__(self):
        self.env = clips.Environment()
        self.env.load('logistics_rules.clp')
        self.env.reset()

    def add_cargo_fact(self, weight, volume, fragile='no', urgent='no', route_risk='low'):
        template = self.env.find_template('cargo')
        fact = template.assert_fact(
            weight=weight,
            volume=volume,
            fragile=clips.Symbol(fragile),
            urgent=clips.Symbol(urgent),
            route_risk=clips.Symbol(route_risk)
        )
        return fact

    def run(self):
        self.env.run()

    def get_transport_decisions(self):
        decisions = []
        for fact in self.env.facts():
            if fact.template.name == 'transport_type':
                decisions.append(fact[0])
        return decisions

    def explain_decisions(self):
        print("\nОбъяснение решений:")
        for rule in self.env.rules():
            if rule.activations:
                print(f"Правило {rule.name} активировано")


# Использование системы
if __name__ == "__main__":
    es = LogisticsExpertSystem()

    # Добавляем данные о грузе
    es.add_cargo_fact(weight=300, volume=2, fragile='yes')
    es.add_cargo_fact(weight=5, volume=0.2, urgent='yes')

    # Запуск системы
    es.run()

    # Результаты
    print("Рекомендуемые типы транспорта:", es.get_transport_decisions())
    es.explain_decisions()
