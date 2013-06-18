# 
#      * Copyright (c)2011 Enterprise Architecture Solutions ltd.
#      * This file is part of Essential Architecture Manager, 
#      * the Essential Architecture Meta Model and The Essential Project.
#      *
#      * Essential Architecture Manager is free software: you can redistribute it and/or modify
#      * it under the terms of the GNU General Public License as published by
#      * the Free Software Foundation, either version 3 of the License, or
#      * (at your option) any later version.
#      *
#      * Essential Architecture Manager is distributed in the hope that it will be useful,
#      * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      * but WITHOUT ANY WARRANTY; without even the implied warranty of
#      * GNU General Public License for more details.
#      *
#      * You should have received a copy of the GNU General Public License
#      * along with Essential Architecture Manager.  If not, see <http://www.gnu.org/licenses/>.
#      * 
#       
# 01.11.2011  	JWC v1.0
#
# resolveInvalidXMLChars.py
# Identify and resolve all characters in the repository that are invalid XML characters.
#
# Execute this script and then select which method to use: 
# removeInvalidCharacters(True) to remove all characters in string slots that have invalid XML characters. 
# removeInvalidCharacters(False) to identify which instances have invalid characters in which slot.

import java
import re
import string
from edu.stanford.smi.protege.model import ValueType

invalidXMLChars = re.compile('([\x00-\x08] | [\x0B-\x0C] | [\x0E-\x1F])')
aTranslateTable = string.maketrans("","")

def treatString(theInstance, theSlot, theStringValue, theIsRemove, theIsMulti):
    """ Treat theStringValue in theSlot on theInstance for invalid XML characters
        If theIsRemove is True, resolve the invalid characters by removing them
        Otherwise just report the invalid string.
        If theIsMulti is True, then this is a multi-cardinality slot, so do a remove/add to reset the string
    """
    # Check whether there are any characters to remove
    charTest = invalidXMLChars.search(theStringValue)
    if charTest != None:
        # We have bad characters to remove
                
        print "* " + theInstance.getDirectType().getName() + " instance: " + theInstance.getOwnSlotValue(kb.getSlot("name")) + ". Slot: " + theSlot.getName() + ", Value: " + theStringValue
        if theIsRemove:
            aValidValue = theStringValue.translate(aTranslateTable, "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0B\x0C\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1F")
            if theIsMulti:
                theInstance.removeOwnSlotValue(theSlot, theStringValue)
                theInstance.addOwnSlotValue(theSlot, aValidValue)
            else:
                theInstance.setOwnSlotValue(theSlot, aValidValue)
        
        
def removeInvalidCharacters(theIsRemove):
    """ Remove all the characters in all instances that are invalid XML characters
    """
    if theIsRemove:
        print "Updating instances: "
    else:
        print "The following instances should be updated to replace invalid XML characters:"
        
    # Get all the simple instances in the repository
    anInstanceList = kb.getInstances()    
    for anInstance in anInstanceList:
        # For each instance, get its slots
        aSlotList = anInstance.getOwnSlots()
        for aSlot in aSlotList:
            # Cycle through these, if they are ValueType.STRING then treat them
            aType = aSlot.getValueType()
            if aType == ValueType.STRING:                
                if aSlot.getAllowsMultipleValues():
                    aStringValueList = anInstance.getDirectOwnSlotValues(aSlot)                    
                    for aStringValue in aStringValueList:
                        if aStringValue != None:
                            treatString(anInstance, aSlot, aStringValue, theIsRemove, True)                        
                else:
                    aStringValue = anInstance.getDirectOwnSlotValue(aSlot)
                    if aStringValue != None:
                        treatString(anInstance, aSlot, aStringValue, theIsRemove, False)                    
                        
                

print "Scripts loaded. You can remove all invalid characters using this script or identify those instances that need attention"
print "type 'removeInvalidCharacters(True)' and press enter to remove all invalid characters from the repository"
print "type 'removeInvalidCharacters(False)' and press enter to identify those instances that need to be manually resolved."
print "No reported instances that need updating indicates that there are no invalid XML characters in the repository."

