#!/usr/bin/env python
"""
Handles mosaic related functionality.

Responsibilities:

 1. Keep track of the current objective.

 2. Output the pixel to nanometer scaling given the current
    objective.


Hazen 01/17
"""

from PyQt5 import QtWidgets

import storm_control.hal4000.halLib.halMessage as halMessage
import storm_control.hal4000.halLib.halModule as halModule
import storm_control.hal4000.qtdesigner.mosaic_ui as mosaicUi


def getObjectiveName(parameters):
    return parameters.get(parameters.get("objective")).split(",")[0]

def getObjectivePixelSize(parameters):
    return float(parameters.get(parameters.get("objective")).split(",")[1])

                     
class MosaicBox(QtWidgets.QGroupBox):

    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.ui = mosaicUi.Ui_GroupBox()
        self.ui.setupUi(self)

    def setObjectiveText(self, text):
        self.ui.objectiveText.setText(text)
        
    
class Mosaic(halModule.HalModule):
    """
    Mosaic settings controller.

    This sends the following messages:
     'pixel size'
    """
    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)

        self.have_stage = False
        self.parameters = module_params.get("parameters")
        
        self.view = MosaicBox()
        self.configure_dict = {"ui_order" : 3,
                               "ui_parent" : "hal.containerWidget",
                               "ui_widget" : self.view}

        # The current pixel size.
        halMessage.addMessage("pixel size")

    def processMessage(self, message):

        if (message.level == 1):
            if (message.getType() == "configure1"):

                # Check if there is a (motorized) stage.
                if "stage" in message.getData():
                    self.have_stage = True
                    
                # Initial UI configuration.
                self.view.setObjectiveText(getObjectiveName(self.parameters))

                # Add view to HAL UI display.
                self.newMessage.emit(halMessage.HalMessage(source = self,
                                                           m_type = "add to ui",
                                                           data = self.configure_dict))

                # Broadcast default parameters.
                self.newMessage.emit(halMessage.HalMessage(source = self,
                                                           m_type = "current parameters",
                                                           data = {"parameters", self.parameters.copy()}))

            elif (message.getType() == "new parameters"):
                p = message.getData().get(self.module_name)
                if (self.parameters.get("objective") != p.get("objective")):
                    objective = p.get("objective")
                    self.parameters.setv("objective", objective)
                    self.view.setObjectiveText(getObjectiveName(self.parameters))
                    if self.have_stage:
                        pixel_size = getObjectivePixelSize(self.parameters)
                        self.newMessage.emit(halMessage.HalMessage(source = self,
                                                                   m_type = "pixel size",
                                                                   data = {"pixel_size" : pixel_size}))

        super().processMessage(message)                    
                    
                    

