> {Variable V} += {Const K}
        {REPEAT K}
        {V} <- {V} + 1
        {END REPEAT}


> {Variable V} -= {Const K}
        {REPEAT K}
        {V} <- {V} - 1
        {END REPEAT}


> GOTO {Label L}
        Z <- Z + 1
        IF Z != 0 GOTO {L}


> IF 0 != 0 GOTO {Label L}
    [E] Y <- Y


> IF {Const K} != 0 GOTO {LABEL L}
        GOTO {L}


> IF {Variable V} = 0 GOTO {Label L}
        IF {V} != 0 GOTO E
        GOTO {L}
    [E] Y <- Y


> {Variable V} <- 0
    [A] {V} <- {V} - 1
        IF {V} != 0 GOTO A


> {Variable V} <- {Numeric N} - {Numeric N}
        {V} <- 0


> {Variable V1} += {Variable V2}
        IF {V2} != 0 GOTO A
        GOTO E
    [A] {V2} <- {V2} - 1
        Z <- Z + 1
        IF {V2} != 0 GOTO A
    [B] Z <- Z - 1
        {V2} <- {V2} + 1
        {V1} <- {V1} + 1
        IF Z != 0 GOTO B
    [E] Y <- Y


> {Variable V1} <- {Variable V1} + {Numeric V2}
        {V1} += {V2}


> {Variable V1} <- {Numeric V2} + {Variable V1}
        {V1} += {V2}


> {Variable V1} <- {Numeric V2}
        {V1} <- 0
        {V1} += {V2}


> {Variable V1} -= {Variable V2}
        IF {V2} = 0 GOTO E
    [A] {V2} <- {V2} - 1
        Z <- Z + 1
        IF {V2} != 0 GOTO A
    [B] Z <- Z - 1
        {V2} <- {V2} + 1
        {V1} <- {V1} - 1
        IF Z != 0 GOTO B
    [E] Y <- Y


> {Variable V1} <- {Variable V1} - {Numeric V2}
        {V1} -= {V2}


> {Variable V1} <- {Numeric V2} - {Variable V1}
        Z <- {V1}
        {V1} <- {V2}
        {V1} -= Z


> {Variable OUT} <- {Numeric V1} + {Numeric V2}
        {OUT} <- {V1}
        {OUT} += {V2}


> {Variable OUT} <- {Numeric V1} - {Numeric V2}
        {OUT} <- {V1}
        {OUT} -= {V2}


> IF {Numeric V} >= {Numeric V} GOTO {Label L}
        GOTO {L}


> IF {Numeric V1} >= {Numeric V2} GOTO {Label L}
        Z <- {V1} + 1
        Z2 <- {V2} + 1
    [A] Z <- Z - 1
        Z2 <- Z2 - 1
        IF Z2 = 0 GOTO {L}
        IF Z != 0 GOTO A


> IF {Numeric V1} <= {Numeric V2} GOTO {Label L}
        IF {V2} >= {V1} GOTO {L}


> IF {Numeric V1} > {Numeric V2} GOTO {Label L}
        IF {V2} >= {V1} GOTO E
        GOTO {L}
    [E] Y <- Y


> IF {Numeric V1} < {Numeric V2} GOTO {Label L}
        IF {V2} > {V1} GOTO {L}


> IF {Numeric V} = {Numeric V} GOTO {Label L}
        GOTO {L}


> IF {Numeric V1} = {Numeric V2} GOTO {Label L}
        Z <- {V1} + 1
        Z2 <- {V2} + 1
    [A] Z <- Z - 1
        Z2 <- Z2 - 1
        IF Z = 0 GOTO B
        IF Z2 = 0 GOTO E
        GOTO A
    [B] IF Z2 = 0 GOTO {L}
    [E] Y <- Y


> IF {Numeric V1} != {Numeric V2} GOTO {Label L}
        IF {V1} = {V2} GOTO E
        GOTO {L}
    [E] Y <- Y


> {Variable V1} *= {Numeric V2}
        IF {V2} != 0 GOTO B
        {V1} <- 0
        GOTO E
    [B] Z <- {V2} - 1
        Z2 <- {V1}
        IF Z = 0 GOTO E
    [A] Z <- Z - 1
        {V1} += Z2
        IF Z != 0 GOTO A
    [E] Y <- Y


> {Variable V1} <- {Variable V1} * {Numeric V2}
        {V1} *= {V2}


> {Variable V1} <- {Numeric V2} * {Variable V1}
        {V1} *= {V2}


> {Variable OUT} <- {Numeric V1} * {Numeric V2}
        {OUT} <- {V1}
        {OUT} *= {V2}


> {Variable OUT} <- {Numeric V1}{Variable V2}
        {OUT} <- {V1} * {V2}


> {Variable OUT} <- {Numeric V1} % {Numeric V2}
    [B] IF {V2} = 0 GOTO B
        Z2 <- {V2}
        {OUT} <- {V1}
    [A] IF {OUT} < Z2 GOTO E
        {OUT} -= Z2
        GOTO A
    [E] Y <- Y


> {Variable V1} %= {Numeric V2}
        {V1} <- {V1} % {V2}


> {Variable OUT} <- {Numeric V1} / {Numeric V2}
    [B] IF {V2} = 0 GOTO B
        Z <- {V1}
        Z2 <- {V2}
        {OUT} <- 0
    [A] IF Z2 > Z GOTO E
        Z -= Z2
        {OUT} <- {OUT} + 1
        GOTO A
    [E] Y <- Y


> {Variable V1} /= {Numeric V2}
        {V1} <- {V1} / {V2}


> IF {Numeric V} IS PRIME GOTO {Label L}
        IF {V} < 2 GOTO E
        Z <- 2
        Z2 <- {V} - 2
    [A] IF Z2 = 0 GOTO {L}
        Z3 <- {V} % Z
        IF Z3 = 0 GOTO E
        Z2 <- Z2 - 1
        Z <- Z + 1
        GOTO A
    [E] Y <- Y


> {Variable OUT} <- PRIME {Numeric V}
        Z2 <- {V}
        {OUT} <- 2
    [A] IF {OUT} IS PRIME GOTO C
    [B] {OUT} <- {OUT} + 1
        GOTO A
    [C] Z2 <- Z2 - 1
        IF Z2 != 0 GOTO B


> {Variable OUT} <- {Numeric V1} ^ {Numeric V2}
        Z <- {V2}
        {OUT} <- 1
        IF Z = 0 GOTO E
    [A] {OUT} *= {V1}
        Z <- Z - 1
        IF Z != 0 GOTO A
    [E] Y <- Y


> {Variable V1} ^= {Numeric V2}
        {V1} <- {V1} ^ {V2}


> {Variable OUT} <- LEFT {Numeric V}
        Z2 <- {V} + 1
        {OUT} <- 0
        Z <- 1
    [A] {OUT} <- {OUT} + 1
        Z *= 2
        Z4 <- Z2 % Z
        IF Z4 = 0 GOTO A
        {OUT} <- {OUT} - 1


> {Variable OUT} <- RIGHT {Numeric V}
        Z <- LEFT {V}
        Z3 <- {V} + 1
        {OUT} <- 2 ^ Z
        {OUT} <- Z3 / {OUT}
        {OUT} <- {OUT} - 1
        {OUT} /= 2


> {Variable OUT} <- LENGTH {Numeric V}
        Z <- {V}
        {OUT} <- 0
        Z2 <- 1
    [A] IF Z = Z2 GOTO E
        {OUT} <- {OUT} + 1
        Z4 <- PRIME {OUT}
    [B] Z5 <- Z % Z4
        IF Z5 != 0 GOTO A
        Z /= Z4
        GOTO B
    [E] Y <- Y


> {Variable OUT} <- {Numeric LIST} AT INDEX {Numeric INDEX}
        Z <- PRIME {INDEX}
        Z2 <- {LIST}
        {OUT} <- 0
    [A] Z3 <- Z2 % Z
        IF Z3 != 0 GOTO E
        {OUT} <- {OUT} + 1
        Z2 /= Z
        GOTO A
    [E] Y <- Y


> {Variable OUT} <- {Numeric INSTRUCTIONS} GET INDEX OF LABEL {Numeric L}
        Z <- LENGTH {INSTRUCTIONS}
        Z2 <- 1
    [A] IF Z2 > Z GOTO E2
        Z3 <- {INSTRUCTIONS} AT INDEX Z2
        Z3 <- LEFT Z3
        Z3 += 2
        IF Z3 != {L} GOTO B
        {OUT} <- Z2
        GOTO E
    [B] Z2 <- Z2 + 1
        GOTO A
    [E2] {OUT} <- 0
    [E] Y <- Y


> MAIN # Universal Function of Order 1
        X2 <- X2 + 1
        Z <- 3 ^ X1

        # At this point, X2 contains the program by list of instruction encodings,
        # and Z contains the list [0, X1, 0, 0, ...],
        # representing the variable values in encoding order
        Z3 <- Z3 + 1 # The instruction index
        Z4 <- LENGTH X2 # The length of the program
    [C] IF Z3 > Z4 GOTO E
        IF Z3 = 0 GOTO E
        Z5 <- X2 AT INDEX Z3 # Z5 <- <a, <b,c>>
        Z5 <- RIGHT Z5 # Z5 <- <b, c>
        Z6 <- RIGHT Z5 # Z6 <- c
        Z6 <- Z6 + 1 # Z6 <- c + 1
        Z6 <- PRIME Z6 # Z6 <- P(c+1)
        Z7 <- LEFT Z5 # b
        IF Z7 = 0 GOTO D
        Z7 <- Z7 - 1
        IF Z7 = 0 GOTO A2
        Z7 <- Z7 - 1
        Z8 <- Z % Z6
        IF Z8 != 0 GOTO D
        IF Z7 = 0 GOTO B2
        Z7 += 2
        Z3 <- X2 GET INDEX OF LABEL Z7
        GOTO C
   [B2] Z /= Z6
        GOTO D
   [A2] Z *= Z6
    [D] Z3 <- Z3 + 1
        GOTO C
    [E] Y <- Z AT INDEX 1
