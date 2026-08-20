import Interpreter as DG
import time

start = time.time()

def main():
    knowledge_base = ["forall p. dropped(p) implies delivered(p)",
                      "exists p. at(3) implies located(charging)",
                      "exists p. at(4) implies located(charging)",
                      "exists p. at(5) implies located(charging)",
                      "battery(1) implies safe1",
                      "battery(2) implies safe1",
                      "exists p. at(p) and not at(15) implies safe2",
                      # Error implication
                      "E1 implies fatal",
                      "E2 implies fatal",
                      "E3 implies fatal",
                      "E4 implies fatal",
                      "equal(0,0)",
                      "equal(1,1)",
                      "equal(2,2)",
                      "equal(3,3)",
                      "equal(4,4)",
                      "equal(5,5)",
                      "equal(6,6)",
                      "equal(7,7)",
                      "equal(8,8)",
                      "equal(9,9)",
                      "equal(10,10)",
                      "equal(11,11)",
                      "equal(12,12)",
                      "equal(13,13)",
                      "equal(14,14)",
                      "equal(15,15)",
                      "equal(A1,A1)",
                      "equal(A2,A2)",
                      "equal(A3,A3)",
                      "equal(_,_)",
                      "equal(charging,charging)"]
    constraints_of_action_generation = [
        # Ensure the decision-making module will not generate decisions before the revision of goals and beliefs when encountering errors.
        "forall p. at(p) and fatal implies M(p)",
        "a-goal-holding and not holding and docked(1) and not nonfatal and not E2 and not fatal implies A(1)",
        "a-goal-holding and not holding and docked(2) and not nonfatal and not E2 and not fatal implies A(2)",
        # From P1 to P0
        "a-goal-at(0) and at(1) and holding and assigned(0) and docked(1) and not fatal implies B1(1,0)",
        "a-goal-at(0) and at(1) and holding and assigned(0) and not docked(1) and not fatal implies B2(1,0)",

        # From P2 to P0
        "a-goal-at(0) and at(2) and assigned(14) and holding and not nonfatal implies B(2,14)",
        "a-goal-at(0) and at(14) and assigned(13) and holding and not nonfatal implies B(14,13)",
        "a-goal-at(0) and at(13) and assigned(11) and holding and not nonfatal implies B(13,11)",
        "a-goal-at(0) and at(11) and assigned(0) and holding and not nonfatal implies B(11,0)",

        # From P0 to P3/4/5
        "a-goal-at(7) and not holding and at(0) and assigned(7) implies B(0,7)",
        "a-goal-at(7) and holding and docking_error and at(0) and assigned(7) implies B(0,7)",
        "a-goal-at(7) and holding and holding_error and at(0) and assigned(7) implies B(0,7)",
        "a-goal-at(6) and at(7) and assigned(6) and not fatal implies B(7,6)",
        "a-goal-at(8) and at(6) and assigned(8) and not fatal implies B(6,8)",
        "forall p. a-goal-located(charging) and not a-goal-delivered(0) and at(8) and assigned(p) and not equal(8,p) implies B(8,p)",

        # From P1 to P3/4/5 (docking or pick error)
        "a-goal-located(charging) and at(1) and assigned(9) and not holding implies B(1,9)",
        "a-goal-at(8) and not holding and at(9) and assigned(8) implies B(9,8)",

        # From P3/4/5 to P1
        "forall p. a-goal-at(1) and located(charging) and at(p) and assigned(8) implies B(p,8)",
        "a-goal-at(1) and at(8) and assigned(9) implies B(8,9)",
        "a-goal-at(1) and at(9) and assigned(1) implies B(9,1)",

        # From P3/4/5 to P2
        "forall p. a-goal-at(2) and located(charging) and at(p) and assigned(10) implies B(p,10)",
        "a-goal-at(2) and at(10) and assigned(12) implies B(10,12)",
        "a-goal-at(2) and at(12) and assigned(2) implies B(12,2)",

        # Request location permission.
        # From location 1 to location 0
        "a-goal-at(0) and at(1) and holding and not fatal and not assigned(0) implies S(0)",
        # From location 0 to location 3/4/5
        "a-goal-at(7) and at(0) and not assigned(7) and not fatal implies S(7)",
        "a-goal-at(6) and at(7) and not assigned(6) and not fatal implies S(6)",
        "a-goal-at(8) and at(6) and not assigned(8) and not fatal implies S(8)",

        # From location 2 to location 0
        "a-goal-at(0) and at(2) and not nonfatal and not assigned(14) and holding and not fatal implies S(14)",
        "a-goal-at(0) and at(14) and not nonfatal and not assigned(13) and holding and not fatal implies S(13)",
        "a-goal-at(0) and at(13) and not nonfatal and not assigned(11) and holding and not fatal implies S(11)",
        "a-goal-at(0) and at(11) and not nonfatal and not assigned(0) and holding and not fatal implies S(0)",

        # From location 3/4/5 to location 1
        "a-goal-at(1) and located(charging) and not assigned(8) and not fatal implies S(8)",
        "a-goal-at(9) and at(8) and not assigned(9) and not fatal implies S(9)",
        "a-goal-at(1) and at(9) and not assigned(1) and not fatal implies S(1)",

        # From location 3/4/5 to location 2
        "a-goal-at(2) and located(charging) and not assigned(10) and not fatal implies S(10)",
        "a-goal-at(12) and at(10) and not assigned(12) and not fatal implies S(12)",
        "a-goal-at(2) and at(12) and not assigned(2) and not fatal implies S(2)",

        "forall p. a-goal-delivered(p) and at(p) and docked(p) and holding and not E3 and not fatal implies D(p)",

        "forall p. a-goal-battery(2) and assigned(p) and battery(1) and docked(p) and not fatal implies E(p)",
        "a-goal-located(charging) and not a-goal-at(0) and at(8) and not fatal implies F",
        "a-goal-located(charging) and not a-goal-at(0) and at(12) and not fatal implies F",
        "exists x,y. reserved(x,y) implies G"
    ]
    enableness_of_actions = [
        "forall p. A(p) implies pickup(p)",

        # From P0 to P3/4/5
        "B(0,7) implies move2(0,7)",
        "B(0,7) implies move2_fail(0,7)",
        "B(7,6) implies move4(7,6)",
        "B(7,6) implies move4_fail(7,6)",
        "B(6,8) implies move4(6,8)",
        "B(6,8) implies move4_fail(6,8)",
        "B(8,3) implies move3(8,3)",
        "B(8,3) implies move3_fail(8,3)",
        "B(8,3) implies move3_fail2(8,3)",
        "B(8,4) implies move3(8,4)",
        "B(8,4) implies move3_fail(8,4)",
        "B(8,4) implies move3_fail2(8,4)",
        "B(8,5) implies move3(8,5)",
        "B(8,5) implies move3_fail(8,5)",
        "B(8,5) implies move3_fail2(8,5)",

        # From docked location P2 to docked location P0
        "B(2,14) implies move2(2,14)",
        "B(2,14) implies move2_fail(2,14)",
        "B(14,13) implies move4(14,13)",

        "B(13,11) implies move4(13,11)",
        #"B(13,11) implies move4_fail(13,11)",
        "B(11,0) implies move3(11,0)",
        # from docked location P1 to docked location P0
        "B1(1,0) implies move1(1,0)",
        "B1(1,0) implies move1_fail(1,0)",
        "B1(1,0) implies move1_fail2(1,0)",

        # From docked location: P3/P4/P5 to P1
        "forall p. located(charging) and B(p,8) and assigned(8) implies move2(p,8)",
        "forall p. located(charging) and B(p,8) and assigned(8) implies move2_fail(p,8)",
        "at(8) and B(8,9) and assigned(9) implies move4(8,9)",
        "at(8) and B(8,9) and assigned(9) implies move4_fail(8,9)",
        "at(9) and B(9,1) and assigned(1) implies move3(9,1)",
        "at(9) and B(9,1) and assigned(1) implies move3_fail(9,1)",
        "at(9) and B(9,1) and assigned(1) implies move3_fail2(9,1)",

        # From docked location: P3/P4/P5 to P2
        "forall p. located(charging) and B(p,10) and assigned(10) implies move2(p,10)",
        "forall p. located(charging) and B(p,10) and assigned(10) implies move2_fail(p,10)",
        "at(10) and B(10,12) and assigned(12) implies move4(10,12)",
        "at(10) and B(10,12) and assigned(12) implies move4_fail(10,12)",
        "at(12) and B(12,2) and assigned(2) implies move3(12,2)",
        "at(12) and B(12,2) and assigned(2) implies move3_fail(12,2)",
        "at(12) and B(12,2) and assigned(2) implies move3_fail2(12,2)",

        "exists p. D(p) implies dropoff(p)",
        "forall p. E(p) implies charging(p)",
        "forall p. E(p) implies charging_fail(p)",
    ]
    sent_message_update = [
        "F implies send!(C) idle(_)",
        "G implies send?(allother) released(_)",
        "forall p. S(p) and not fatal implies send!(C) idle(p)",
        "forall y. M(y) implies send!(C) at(y)"
    ]

    event_processing = [
        # Fatal Error handling
        "E1 implies insert docking_error",
        "E2 implies insert pick_error",
        "E3 implies insert holding_error",
        "E4 implies insert charging_error",
        "fatal implies drop allgoals",
        "fatal implies delete all",
        "located(charging) and pick_error implies delete pick_error",
        # Fix error rules
        "exists x. holding and located(charging) and holding_error implies delete holding",
        "located(charging) and holding_error implies delete holding_error",
        "exists x. holding and located(charging) and docking_error implies delete holding",
        "located(charging) and docking_error implies delete docking_error",
        # Remove temporary goals
        "exists p. at(p) and dropped(0) and not equal(p,0) implies delete dropped(0)",

        # Release location permission for the fatal agent
        "forall z. exists x,y. sent!(x) at(y) and reserved(x,z) implies insert idle(z)",
        "forall x,z. exists y. sent!(x) at(y) and reserved(x,z) implies delete reserved(x,z)",
        # Normal event processing
        "forall x,z in D2 . exists y. sent!(x) idle(y) and idle(y) and not reserved(z,y) implies insert reserved(x,y)",
        "forall x. exists y. sent!(x) idle(y) and reserved(x,y) implies send:(x) assigned(y)",
        "forall y. exists x,z. sent!(x) idle(y) and reserved(z,y) and equal(x,z) implies delete idle(y)",
        "forall x,y. sent?(x) released(_) and released(y) implies send:(x) idle(y)",
        "forall y. exists x. sent?(x) released(_) and released(y) implies delete released(y)",
        "forall y. exists x. sent:(x) idle(y) implies insert idle(y)",
        "forall y. exists x. sent:(x) idle(y) implies delete reserved(x,y)",
        "forall x,z in D2 ,m in D1 . sent!(x) idle(_) and idle(3) and not reserved(z,3) and not reserved(x,m) implies insert reserved(x,3)",
        "forall x. sent!(x) idle(_) and idle(3) and reserved(x,3) implies send:(x) assigned(3)",
        "exists x. sent!(x) idle(_) and reserved(x,3) implies delete idle(3)",
        "forall x,z in D2 ,m in D1 . sent!(x) idle(_) and idle(4) and not reserved(z,4) and not reserved(x,m) implies insert reserved(x,4)",
        "forall x. sent!(x) idle(_) and idle(4) and reserved(x,4) implies send:(x) assigned(4)",
        "exists x. sent!(x) idle(_) and reserved(x,4) implies delete idle(4)",
        "forall x,z in D2 ,m in D1 . sent!(x) idle(_) and idle(5) and not reserved(z,5) and not reserved(x,m) implies insert reserved(x,5)",
        "forall x. sent!(x) idle(_) and idle(5) and reserved(x,5) implies send:(x) assigned(5)",
        "exists x. sent!(x) idle(_) and reserved(x,5) implies delete idle(5)",
        "forall y. exists x. sent:(x) assigned(y) implies insert assigned(y)",
        "forall p. exists s. a-goal-transport(s,p) implies adopt delivered(p)",
        "forall s. exists p. a-goal-transport(s,p) implies adopt at(s)",
        "forall p. exists s. a-goal-transport(s,p) implies adopt at(p)",
        "exists s,p. a-goal-delivered(p) implies adopt located(charging)",
        "exists p. a-goal-delivered(p) and not holding implies adopt holding",
        "forall s,p. a-goal-transport(s,p) implies drop transport(s,p)",

        # From location 0 to location 3/4/5
        "a-goal-located(charging) and at(0) implies adopt at(7)",
        "a-goal-located(charging) and at(7) and not a-goal-at(0) implies adopt at(6)",
        "a-goal-located(charging) and at(6) and not a-goal-at(0) implies adopt at(8)",

        # From location 2 to location 0
        "a-goal-at(0) and at(2) and holding implies adopt at(14)",
        "a-goal-at(0) and at(14) and holding implies adopt at(13)",
        "a-goal-at(0) and at(13) and holding implies adopt at(11)",
        #"a-goal-at(0) and at(11) and holding implies adopt at(1)",

        # From location 3/4/5 to location 1
        "a-goal-at(1) and located(charging) implies adopt at(8)",
        "a-goal-at(1) and at(8) implies adopt at(9)",
        # From location 3/4/5 to location 2
        "a-goal-at(2) and located(charging) implies adopt at(10)",
        "a-goal-at(2) and at(10) implies adopt at(12)",

        # Add charging goals
        "at(3) and battery(1) implies adopt battery(2)",
        "at(4) and battery(1) implies adopt battery(2)",
        "at(5) and battery(1) implies adopt battery(2)"
    ]
    action_specification = {
        "pickup": "pickup and not holding implies holding",

        "dropoff": "forall p. dropoff(p) and holding implies dropped(p) and not holding",

        # move1: from docked station to docked station
        "move1": "forall x,y. move1(x,y) and at(x) and docked(x) implies at(y) and not at(x) and not docked(x) and docked(y) and not assigned(x) and released(x)",
        #"move1_fail": "exists x,y. move1_fail(x,y) implies E5",
        #"move1_fail2": "exists x,y. move1_fail2(x,y) implies E1",
        # move2: from docked station to non-docked station
        "move2": "forall x,y. move2(x,y) and at(x) and docked(x) implies at(y) and not at(x) and not docked(x) and not assigned(x) and released(x)",
        #"move2_fail": "exists x,y. move2_fail(x,y) implies E5",
        # move3: from non-docked station to docked station
        "move3": "forall x,y. move3(x,y) and at(x) implies at(y) and not at(x) and docked(y) and not assigned(x) and released(x)",
        #"move3_fail": "exists x,y. move3_fail(x,y) implies E5",
        #"move3_fail2": "exists x,y. move3_fail2(x,y) implies E1",
        # move4: from non-docked station to non-docked station
        "move4": "forall x,y. move4(x,y) and at(x) implies at(y) and not at(x) and not assigned(x) and released(x)",
        #"move4_fail": "exists x,y. move4_fail(x,y) implies E5",

        "charging": "exists p. charging(p) and battery(1) implies battery(2) and not battery(1)",
        "charging_fail": "exists p. charging(p) and battery(1) implies E4"
    }
    domain = {"D1": ["3", "4", "5"], "D2": ["A1", "A2", "A3"]}
    constants = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "charging",
                 "allother", "all", '_', "A1", "A2", "A3", "C", "D"]
    belief_base4 = ["idle(0)", "idle(1)", "idle(2)", "reserved(A1,3)", "reserved(A2,4)", "reserved(A3,5)",
                    "idle(6)", "idle(7)", "idle(8)", "idle(9)", "idle(10)", "idle(11)", "idle(12)", "idle(13)",
                    "idle(14)", "idle(15)"]
    goal_base1 = ['transport(1,0)']
    goal_base2 = ['transport(2,0)']
    goals1 = [goal_base1]
    goals2 = [goal_base2]
    goals3 = [goal_base1]
    goals4 = []
    dummy_agents = ["C"]
    safety = {"A1": ["safe1", "safe2"], "A2": ["safe1", "safe2"], "A3": ["safe1", "safe2"]}
    A1 = DG.Agent("A1", [], goals1)
    A2 = DG.Agent("A2", [], goals2)
    A3 = DG.Agent("A3", [], goals2)
    C = DG.Agent("C", belief_base4, goals4)
    Agents = [A1,A2,A3,C]
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

