(set-logic QF_LRA)
(declare-fun G0 () Real)
(declare-fun G1 () Real)
(declare-fun G2 () Real)
(declare-fun U0_0 () Real)
(declare-fun V0_0 () Real)
(declare-fun D0_0 () Real)
(declare-fun U0_1 () Real)
(declare-fun V0_1 () Real)
(declare-fun D0_1 () Real)
(declare-fun U0_2 () Real)
(declare-fun V0_2 () Real)
(declare-fun D0_2 () Real)
(declare-fun U1_0 () Real)
(declare-fun V1_0 () Real)
(declare-fun D1_0 () Real)
(declare-fun U1_1 () Real)
(declare-fun V1_1 () Real)
(declare-fun D1_1 () Real)
(declare-fun U1_2 () Real)
(declare-fun V1_2 () Real)
(declare-fun D1_2 () Real)
(declare-fun U2_0 () Real)
(declare-fun V2_0 () Real)
(declare-fun D2_0 () Real)
(declare-fun U2_1 () Real)
(declare-fun V2_1 () Real)
(declare-fun D2_1 () Real)
(declare-fun U2_2 () Real)
(declare-fun V2_2 () Real)
(declare-fun D2_2 () Real)
(declare-fun CU0_0 () Real)
(declare-fun CV0_0 () Real)
(declare-fun CD0_0 () Real)
(declare-fun CU0_1 () Real)
(declare-fun CV0_1 () Real)
(declare-fun CD0_1 () Real)
(declare-fun CU0_2 () Real)
(declare-fun CV0_2 () Real)
(declare-fun CD0_2 () Real)
(assert (>= G0 0.0))
(assert (>= G1 0.0))
(assert (>= G2 0.0))
(assert (>= U0_0 0.0))
(assert (>= V0_0 0.0))
(assert (>= D0_0 0.0))
(assert (>= U0_1 0.0))
(assert (>= V0_1 0.0))
(assert (>= D0_1 0.0))
(assert (>= U0_2 0.0))
(assert (>= V0_2 0.0))
(assert (>= D0_2 0.0))
(assert (>= U1_0 0.0))
(assert (>= V1_0 0.0))
(assert (>= D1_0 0.0))
(assert (>= U1_1 0.0))
(assert (>= V1_1 0.0))
(assert (>= D1_1 0.0))
(assert (>= U1_2 0.0))
(assert (>= V1_2 0.0))
(assert (>= D1_2 0.0))
(assert (>= U2_0 0.0))
(assert (>= V2_0 0.0))
(assert (>= D2_0 0.0))
(assert (>= U2_1 0.0))
(assert (>= V2_1 0.0))
(assert (>= D2_1 0.0))
(assert (>= U2_2 0.0))
(assert (>= V2_2 0.0))
(assert (>= D2_2 0.0))
(assert (>= CU0_0 0.0))
(assert (>= CV0_0 0.0))
(assert (>= CD0_0 0.0))
(assert (>= CU0_1 0.0))
(assert (>= CV0_1 0.0))
(assert (>= CD0_1 0.0))
(assert (>= CU0_2 0.0))
(assert (>= CV0_2 0.0))
(assert (>= CD0_2 0.0))
(assert (= (+ 0.0
      G0
      G1
      G2
      U0_0
      V0_0
      D0_0
      U0_1
      V0_1
      D0_1
      U0_2
      V0_2
      D0_2
      U1_0
      V1_0
      D1_0
      U1_1
      V1_1
      D1_1
      U1_2
      V1_2
      D1_2
      U2_0
      V2_0
      D2_0
      U2_1
      V2_1
      D2_1
      U2_2
      V2_2
      D2_2
      CU0_0
      CV0_0
      CD0_0
      CU0_1
      CV0_1
      CD0_1
      CU0_2
      CV0_2
      CD0_2)
   15.0))
(assert (>= (+ 0.0 D0_0 U0_0 V0_0) 2.0))
(assert (>= (+ 0.0 G2 U0_0 V0_0) 2.0))
(assert (>= (+ 0.0 G1 G2 U0_0) 1.0))
(assert (>= (+ 0.0 D0_1 U0_1 V0_1) 2.0))
(assert (>= (+ 0.0 G0 U0_1 V0_1) 2.0))
(assert (>= (+ 0.0 G0 G2 U0_1) 1.0))
(assert (>= (+ 0.0 D0_2 U0_2 V0_2) 2.0))
(assert (>= (+ 0.0 G1 U0_2 V0_2) 2.0))
(assert (>= (+ 0.0 G0 G1 U0_2) 1.0))
(assert (>= (+ 0.0 D1_0 U1_0 V1_0) 1.0))
(assert (>= (+ 0.0 G2 U1_0 V1_0) 1.0))
(assert (>= (+ 0.0 U1_0 V0_1 V0_2) 2.0))
(assert (>= (+ 0.0 U0_1 U0_2 V1_0) 3.0))
(assert (>= (+ 0.0 D1_1 U1_1 V1_1) 1.0))
(assert (>= (+ 0.0 G0 U1_1 V1_1) 1.0))
(assert (>= (+ 0.0 U1_1 V0_0 V0_2) 2.0))
(assert (>= (+ 0.0 U0_0 U0_2 V1_1) 3.0))
(assert (>= (+ 0.0 D1_2 U1_2 V1_2) 1.0))
(assert (>= (+ 0.0 G1 U1_2 V1_2) 1.0))
(assert (>= (+ 0.0 U1_2 V0_0 V0_1) 2.0))
(assert (>= (+ 0.0 U0_0 U0_1 V1_2) 3.0))
(assert (>= (+ 0.0 D2_0 U2_0 V2_0) 1.0))
(assert (>= (+ 0.0 G2 U2_0 V2_0) 1.0))
(assert (>= (+ 0.0 U2_0 V1_1 V1_2) 2.0))
(assert (>= (+ 0.0 U1_1 U1_2 V2_0) 1.0))
(assert (>= (+ 0.0 D2_1 U2_1 V2_1) 1.0))
(assert (>= (+ 0.0 G0 U2_1 V2_1) 1.0))
(assert (>= (+ 0.0 U2_1 V1_0 V1_2) 2.0))
(assert (>= (+ 0.0 U1_0 U1_2 V2_1) 1.0))
(assert (>= (+ 0.0 D2_2 U2_2 V2_2) 1.0))
(assert (>= (+ 0.0 G1 U2_2 V2_2) 1.0))
(assert (>= (+ 0.0 U2_2 V1_0 V1_1) 2.0))
(assert (>= (+ 0.0 U1_0 U1_1 V2_2) 1.0))
(assert (>= (+ 0.0 CD0_0 CU0_0 CV0_0) 1.0))
(assert (>= (+ 0.0 CU0_0 CV0_0 G2) 1.0))
(assert (>= (+ 0.0 CU0_0 G2 V2_0) 1.0))
(assert (>= (+ 0.0 CV0_0 G2 U2_0) 1.0))
(assert (>= (+ 0.0 CD0_1 CU0_1 CV0_1) 1.0))
(assert (>= (+ 0.0 CU0_1 CV0_1 G0) 1.0))
(assert (>= (+ 0.0 CU0_1 G0 V2_1) 1.0))
(assert (>= (+ 0.0 CV0_1 G0 U2_1) 1.0))
(assert (>= (+ 0.0 CD0_2 CU0_2 CV0_2) 1.0))
(assert (>= (+ 0.0 CU0_2 CV0_2 G1) 1.0))
(assert (>= (+ 0.0 CU0_2 G1 V2_2) 1.0))
(assert (>= (+ 0.0 CV0_2 G1 U2_2) 1.0))
(assert (let ((a!1 (distinct U1_0 (+ (+ 0.0 (- U0_1 1.0) (- U0_2 1.0)) 0.0)))
      (a!2 (distinct V1_0 (- 1.0 (+ 0.0 (- U0_1 1.0) (- U0_2 1.0)))))
      (a!3 (+ (+ (+ 0.0 (- U0_0 1.0)) (- U0_2 1.0)) 0.0))
      (a!4 (- 1.0 (+ (+ 0.0 (- U0_0 1.0)) (- U0_2 1.0))))
      (a!5 (+ (+ (+ 0.0 (- U0_0 1.0)) (- U0_1 1.0)) 0.0))
      (a!6 (- 1.0 (+ (+ 0.0 (- U0_0 1.0)) (- U0_1 1.0))))
      (a!7 (+ 0.0
              (+ (+ 0.0 (- U0_0 1.0)) (- U0_2 1.0))
              (+ (+ 0.0 (- U0_0 1.0)) (- U0_1 1.0))))
      (a!8 (+ 0.0 (+ 0.0 (- U0_1 1.0) (- U0_2 1.0)))))
(let ((a!9 (+ a!8 (+ (+ 0.0 (- U0_0 1.0)) (- U0_1 1.0))))
      (a!10 (+ a!8 (+ (+ 0.0 (- U0_0 1.0)) (- U0_2 1.0)))))
  (or (distinct 0.0 G0)
      (distinct 0.0 G1)
      (distinct 0.0 G2)
      (distinct U0_0 (+ (- U0_0 1.0) 1.0))
      (distinct V0_0 (- 1.0 (- U0_0 1.0)))
      (distinct 0.0 D0_0)
      (distinct U0_1 (+ (- U0_1 1.0) 1.0))
      (distinct V0_1 (- 1.0 (- U0_1 1.0)))
      (distinct 0.0 D0_1)
      (distinct U0_2 (+ (- U0_2 1.0) 1.0))
      (distinct V0_2 (- 1.0 (- U0_2 1.0)))
      (distinct 0.0 D0_2)
      a!1
      a!2
      (distinct 0.0 D1_0)
      (distinct U1_1 a!3)
      (distinct V1_1 a!4)
      (distinct 0.0 D1_1)
      (distinct U1_2 a!5)
      (distinct V1_2 a!6)
      (distinct 0.0 D1_2)
      (distinct U2_0 (+ a!7 0.0))
      (distinct V2_0 (- 1.0 a!7))
      (distinct 0.0 D2_0)
      (distinct U2_1 (+ a!9 0.0))
      (distinct V2_1 (- 1.0 a!9))
      (distinct 0.0 D2_1)
      (distinct U2_2 (+ a!10 0.0))
      (distinct V2_2 (- 1.0 a!10))
      (distinct 0.0 D2_2)
      (distinct CU0_0 a!7)
      (distinct CV0_0 (- 1.0 a!7))
      (distinct 0.0 CD0_0)
      (distinct CU0_1 a!9)
      (distinct CV0_1 (- 1.0 a!9))
      (distinct 0.0 CD0_1)
      (distinct CU0_2 a!10)
      (distinct CV0_2 (- 1.0 a!10))
      (distinct 0.0 CD0_2)))))

(check-sat)
