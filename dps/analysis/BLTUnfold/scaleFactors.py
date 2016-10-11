class scaleFactor:
    def __init__( self, etaLowEdge, etaHighEdge, ptLowEdge, ptHighEdge, factor ):
        self.etaLowEdge = str(etaLowEdge)
        self.etaHighEdge = str(etaHighEdge)
        self.ptLowEdge = str(ptLowEdge)
        self.ptHighEdge = str(ptHighEdge)
        self.factor = str(factor)
        pass

        
muon8TeVScaleFactors = [
                    scaleFactor( 0, 0.9, 10, 20, 0.912386496723 ),
                    scaleFactor( 0, 0.9, 25, 30, 0.972452055282 ),
                    scaleFactor( 0, 0.9, 30, 35, 0.970834089244 ),
                    scaleFactor( 0, 0.9, 20, 25, 0.965862226978 ),
                    scaleFactor( 0, 0.9, 60, 90, 0.972944008855 ),
                    scaleFactor( 0, 0.9, 50, 60, 0.972142437533 ),
                    scaleFactor( 0, 0.9, 40, 50, 0.970196629776 ),
                    scaleFactor( 0, 0.9, 90, 140, 0.984919198606 ),
                    scaleFactor( 0, 0.9, 35, 40, 0.971533870084 ),
                    scaleFactor( 0, 0.9, 140, 300, 0.997372291394 ),
                    scaleFactor( 0.9, 1.2, 10, 20, 0.950076238802 ),
                    scaleFactor( 0.9, 1.2, 25, 30, 0.963613089993 ),
                    scaleFactor( 0.9, 1.2, 30, 35, 0.959083862361 ),
                    scaleFactor( 0.9, 1.2, 20, 25, 0.980396102182 ),
                    scaleFactor( 0.9, 1.2, 60, 90, 0.949572545054 ),
                    scaleFactor( 0.9, 1.2, 50, 60, 0.955914704027 ),
                    scaleFactor( 0.9, 1.2, 40, 50, 0.957735548464 ),
                    scaleFactor( 0.9, 1.2, 90, 140, 0.974531465976 ),
                    scaleFactor( 0.9, 1.2, 35, 40, 0.95863318261 ),
                    scaleFactor( 0.9, 1.2, 140, 300, 0.983740867212 ),
                    scaleFactor( 1.2, 2.1, 10, 20, 0.989958505637 ),
                    scaleFactor( 1.2, 2.1, 25, 30, 1.00650756009 ),
                    scaleFactor( 1.2, 2.1, 30, 35, 1.00196917262 ),
                    scaleFactor( 1.2, 2.1, 20, 25, 0.990402317676 ),
                    scaleFactor( 1.2, 2.1, 60, 90, 0.981360591419 ),
                    scaleFactor( 1.2, 2.1, 50, 60, 0.986171182488 ),
                    scaleFactor( 1.2, 2.1, 40, 50, 0.991245531521 ),
                    scaleFactor( 1.2, 2.1, 90, 140, 1.00374013398 ),
                    scaleFactor( 1.2, 2.1, 35, 40, 0.994337896106 ),
                    scaleFactor( 1.2, 2.1, 140, 300, 0.965619755393 ),
                    scaleFactor( 2.1, 2.4, 10, 20, 1.12236018183 ),
                    scaleFactor( 2.1, 2.4, 25, 30, 1.09821221889 ),
                    scaleFactor( 2.1, 2.4, 30, 35, 1.07688652489 ),
                    scaleFactor( 2.1, 2.4, 20, 25, 1.1134083821 ),
                    scaleFactor( 2.1, 2.4, 60, 90, 0.992520345769 ),
                    scaleFactor( 2.1, 2.4, 50, 60, 1.00908832239 ),
                    scaleFactor( 2.1, 2.4, 40, 50, 1.0267340195 ),
                    scaleFactor( 2.1, 2.4, 90, 140, 1.04942096158 ),
                    scaleFactor( 2.1, 2.4, 35, 40, 1.04866260908 ),
                    scaleFactor( 2.1, 2.4, 140, 300, 0.894756597947 ),
                    # Dummy scale factors for where none are provided
                    scaleFactor( 0, 2.4, 300, 1000000, 1 ), # High pt
                    scaleFactor( 2.4, 10, 10, 1000000, 1 ), # Large eta
                    ]


muon7TeVScaleFactors = [
                    scaleFactor( 1.2, 10, 10, 20, 0.994514170516 ),
                    scaleFactor( 1.2, 10, 80, 250, 0.990876331253 ),
                    scaleFactor( 1.2, 10, 20, 30, 1.0014788215 ),
                    scaleFactor( 1.2, 10, 50, 60, 0.998511209452 ),
                    scaleFactor( 1.2, 10, 40, 50, 1.00204337349 ),
                    scaleFactor( 1.2, 10, 60, 80, 0.994487765818 ),
                    scaleFactor( 1.2, 10, 30, 40, 1.00232011278 ),
                    scaleFactor( 0, 1.2, 10, 20, 0.964435887378 ),
                    scaleFactor( 0, 1.2, 80, 250, 0.996798528141 ),
                    scaleFactor( 0, 1.2, 20, 30, 0.979669551678 ),
                    scaleFactor( 0, 1.2, 50, 60, 0.991581251912 ),
                    scaleFactor( 0, 1.2, 40, 50, 0.992806774333 ),
                    scaleFactor( 0, 1.2, 60, 80, 0.991186501183 ),
                    scaleFactor( 0, 1.2, 30, 40, 0.987894599962 ),
                    scaleFactor( 1.2, 10, 250, 1000000, 1 ),
                    # Dummy scale factors for where none are provided
                    scaleFactor( 0, 10, 250, 1000000, 1 ), # High pt
                    ]

electron8TeVScaleFactors = [
                            scaleFactor( 0, 0.8, 20, 30, 0.949*0.987),
                            scaleFactor( 0, 0.8, 30, 40, 0.939*0.987),
                            scaleFactor( 0, 0.8, 40, 50, 0.950*0.997),
                            scaleFactor( 0, 0.8, 50, 200, 0.957*0.998),
                            scaleFactor( 0.8, 1.478, 20, 30, 0.990*0.964),
                            scaleFactor( 0.8, 1.478, 30, 40, 0.920*0.964),
                            scaleFactor( 0.8, 1.478, 40, 50, 0.949*0.980),
                            scaleFactor( 0.8, 1.478, 50, 200, 0.959*0.988),
                            scaleFactor( 1.478, 2.5, 20, 30, 0.857*1.004),
                            scaleFactor( 1.478, 2.5, 30, 40, 0.907*1.004),
                            scaleFactor( 1.478, 2.5, 40, 50, 0.937*1.033),
                            scaleFactor( 1.478, 2.5, 50, 200, 0.954*0.976),
                            # Dummy scale factors for where none are provided
                            scaleFactor( 0, 2.5, 200, 1000000, 1 ), # High pt
                            scaleFactor( 2.5, 10, 20, 1000000, 1 ), # Large eta
                            ]