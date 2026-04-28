from orka import OrkaAgent


agent = OrkaAgent("config.json")
print(agent.run("create customer and send email"))
