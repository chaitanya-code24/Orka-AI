from orka import OrkaAgent


agent = OrkaAgent("config.json")
print(agent.run("create customer Alice in Pune and send email to alice@example.com message Welcome Alice"))
