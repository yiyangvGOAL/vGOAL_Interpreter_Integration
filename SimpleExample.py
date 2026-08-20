import Interpreter as DG
import time

start = time.time()

def main():
    knowledge_base = [
                      "equal(1,1)",
                      "equal(2,2)",
                      "equal(3,3)",
                      "equal(A1,A1)"]
    constraints_of_action_generation = [

    ]
    enableness_of_actions = [

    ]
    sent_message_update = [
    ]

    event_processing = [
        # Fatal Error handling
        "E1 implies insert docking_error",
    ]
    action_specification = {
        "move_succ": "forall x,y. move(x,y) and at(x)  implies at(y) and not at(x)",
        "move_fail": "exists x,y. move1_fail(x,y) implies move_error",
    }
    domain = {}
    constants = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "charging",
                 "allother", "all", '_', "A1", "A2", "A3", "C", "D"]
    goal_base1 = ['at(2)']
    goals1 = [goal_base1]

    safety = {"A1": ["safe1", "safe2"]}
    A1 = DG.Agent("A1", [], goals1)
    Agents = [A1]
    prior_beliefs = []
    agent_test = DG.interpreter(Agents, knowledge_base, constraints_of_action_generation,
                                enableness_of_actions, action_specification, sent_message_update,
                                event_processing, domain, constants, dummy_agents, safety, prior_beliefs)

    end = time.time()
    f = open("Record01.txt", "w+")
    f.write("The duration time is :" + str(end - start))
    f.close()

if __name__ == '__main__':
    main()

