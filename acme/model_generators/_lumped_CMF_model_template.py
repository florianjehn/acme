# -*- coding: utf-8 -*-
"""
Created on Aug 17 09:04 2017
@author(s): Florian U. Jehn

This template is called from the generator to be used as basis for all
models which are generated during the evolutio process. Also the class is
the interface to spotpy.
"""
import datetime
import cmf
import spotpy
import os
import numpy as np
import _lookup


class LumpedModelCMF:
    def __init__(self, genotype, area_catchment, obj_func=None):
        """

        :param genotype:
        """
        if obj_func is None:
            obj_func = _lookup.get_obj_func("nashsutcliffe")
        self.genotype_to_structure(genotype)
        self.objective_function = obj_func
        self.area_catchment = area_catchment
        pass

    def genotype_to_structure(self, genotype):
        """

        :param genotype:
        :return:
        """
        pass

    def loadPETQ(self):
        """
        Lädt Klima und Abfluss aus den entsprechenden Dateien fnQ, fnT, fnP

        MP111 - Änderungsbedarf: Eigentlich keiner
        Verständlichkeit: gut

        Reference: http://fb09-pasig.umwelt.uni-giessen.de/cmf/wiki/CmfTutTestData

        """
        # Fester Modell-Startpunkt
        begin = datetime.datetime(1979, 1, 1)
        step = datetime.timedelta(days=1)
        # Leere Zeitreihen
        P = cmf.timeseries(begin, step)
        P.extend(float(Pstr) for Pstr in open(fnP))

        Q = cmf.timeseries(begin, step)
        Q.extend(float(Qstr) for Qstr in open(fnQ))
        # Convert m3/s to mm/day

        Q *= 86400 * 1e3 / (self.area_catchment * 1e6)
        T = cmf.timeseries(begin, step)
        Tmin = cmf.timeseries(begin, step)
        Tmax = cmf.timeseries(begin, step)

        # Durchlaufen der Zeilen in der Datei
        for line in open(fnT):
            columns = line.split('\t')
            if len(columns) == 3:
                Tmax.add(float(columns[0]))
                Tmin.add(float(columns[1]))
                T.add(float(columns[2]))

        return P, T, Tmin, Tmax, Q
    # TODO: Anpassen an ACME

    def makestations(self, P, T, Tmin, Tmax):
        """
        Erzeugt die Regenfall und Klimastation
        P = Zeitreihe Niederschlag
        T, Tmin, Tmax = Zeitreihe Tägliche Mitteltemperatur, Min und Max

        MP111 - Änderungsbedarf: Eigentlich keiner
        Verständlichkeit: gut

        Reference: http://fb09-pasig.umwelt.uni-giessen.de/cmf/wiki/CmfTutMeteostation
        """
        rainstation = self.project.rainfall_stations.add('Grebenau avg', P,
                                                         (0, 0, 0))
        self.project.use_nearest_rainfall()

        # Temperaturdaten
        meteo = self.project.meteo_stations.add_station('Grebenau avg',
                                                        (0, 0, 0))
        meteo.T = T
        meteo.Tmin = Tmin
        meteo.Tmax = Tmax
        self.project.use_nearest_meteo()

        return rainstation
    # TODO: Anpassen an ACME


    def setparameters(self, tr, Vr=0.0, V0=1000., beta=1.0, ETV1=500.,
                      fETV0=0.0, initVol=100.):
        """
        Setzt die Parameter, dabei werden parametrisierte Verbindungen neu erstellt

        MP111 - Änderungsbedarf: Sehr groß, hier werden alle Parameter des Modells gesetzt
        Verständlichkeit: mittel

        """
        # Ein paar Abkürzungen um Tipparbeit zu sparen
        c = self.project[0]
        outlet = self.outlet

        # Setze den Water-Uptakestress
        c.set_uptakestress(cmf.VolumeStress(ETV1, ETV1 * fETV0))
        cmf.kinematic_wave(c.layers[0], outlet, tr / V0, exponent=beta,
                           residual=Vr, V0=V0)
        c.layers[0].volume = initVol
        # TODO: Anpassen an ACME

    def runmodel(self, verbose=False):
        """
        Startet das Modell

        verbose = Wenn verbose = True, dann wird zu jedem Tag etwas ausgegeben

        MP111 - Änderungsbedarf: Gering, kann so bleiben, kann aber auch
                        um andere Ergebniszeitreihen ergänzt werden. Achtung,
                        falls ihr mehrere Outlets benutzt
        Verständlichkeit: gut

        Reference: http://fb09-pasig.umwelt.uni-giessen.de/cmf/wiki/CmfTutFluxes
        """
        # Erzeugt ein neues Lösungsverfahren
        solver = cmf.ImplicitEuler(self.project, 1e-9)
        # Verkürzte schreibweise für die Zelle - spart tippen
        c = self.project[0]

        # Neue Zeitreihe für Modell-Ergebnisse (res - result)
        resQ = cmf.timeseries(self.begin, cmf.day)
        # Starte den solver und rechne in Tagesschritten
        for t in solver.run(self.project.meteo_stations[0].T.begin, self.end,
                            cmf.day):
            # Fülle die Ergebnisse
            if t >= self.begin:
                resQ.add(self.outlet.waterbalance(t))
            # Gebe eine Statusmeldung auf den Bildschirm aus,
            # dann weiß man wo der solver gerade ist
            if verbose:
                print(t, 'Q=%5.3f, P=%5.3f' % (resQ[t], c.get_rainfall(t)))
        # Gebe die gefüllten Ergebnis-Zeitreihen zurück
        return resQ
    # TODO: anpassen an ACME


    def evaluation(self):
        """
        Gehört auch zum spotpy-Interface.

        MP111 - Änderungsbedarf: Keiner
        Verständlichkeit: Schlecht
        """
        return np.array(
            self.Q[self.begin:self.end + datetime.timedelta(days=1)])
        # TODO: anpassen an ACME


    def parameters(self):
        """
        Gehört auch zum spotpy-Interface.

        MP111 - Änderungsbedarf: Keiner
        Verständlichkeit: Schlecht
        """
        return spotpy.parameter.generate(self.params)
        # TODO: anpassen an ACME

    def objectivefunction(self, simulation, evaluation):
        """
        Gehört auch zum spotpy-Interface.

        MP111 - Änderungsbedarf: Keiner
        Verständlichkeit: Mittel
        """
        return self.objective_function(evaluation, simulation)
        # TODO: anpassen an ACME
