from dataclasses import dataclass
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
import os

def clearScreen():
  print("attempt clear")
  os.system('cls' if os.name == 'nt' else 'clear')
  
allowedFieldTypes = ["int", "str", "bool", "float"]

@dataclass
class MenuForm:
  title: str
  entries: list
  actions: list = None
  hoveredEntry: int = None
  
  def entryStatesToNone(self):
    for entry in self.entries:
      entry.state = None
      
  def entryStateSetHover(self, index):
    self.entryStatesToNone()
    self.hoveredEntry = index
    self.entries[index].state = "hover"
    
  def hoverNextEntry(self):
    if self.hoveredEntry == len(self.entries) - 1:
      self.entryStateSetHover(0)
    else:
      self.hoveredEntry += 1
      self.entryStateSetHover(self.hoveredEntry)
    self.printMenu()
      
  def hoverPreviousEntry(self):
    if self.hoveredEntry == 0:
      self.entryStateSetHover(len(self.entries) - 1)
    else:
      self.hoveredEntry -= 1
      self.entryStateSetHover(self.hoveredEntry)
    self.printMenu()

  def triggerHovered(self):
    self.entries[hoveredEntry].trigger()
  
  def printMenu(self):
    clearScreen()
    if self.hoveredEntry == None:
      self.entryStateSetHover(0)
    menuList = "\n"
    for entry in self.entries:
      menuList += entry.printEntryRow()
    print(Panel(menuList, title=self.title, subtitle="Press the arrow keys to make a selection."))
      
  def handleKeyboardInput(self):
    while True:
      menuInput = input()
      if menuInput == "u":
        self.hoverPreviousEntry()
      if menuInput == "d":
        self.hoverNextEntry()
      if menuInput == "s":
        self.trigger()
      if menuInput == "q":
        exit()
 
  def showInterface(self):
    self.printMenu()
    self.handleKeyboardInput()
    
  def trigger(self):
    output = []
    currentlyHovered = self.entries[self.hoveredEntry]
    if isinstance(currentlyHovered, MenuEntryWritableField):
      currentlyHovered.promptFieldInput()
      self.printMenu()
    if isinstance(currentlyHovered, MenuEntryWriteObjectAttr):
      currentlyHovered.promptFieldInput()
      currentlyHovered.assignFieldValueToObject()
      self.printMenu()
    elif isinstance(currentlyHovered, MenuEntry):
      for entry in self.entries:
        output.append(dict(entry))
      print(output)
      return output


class MenuEntry:
  def __init__(self, fieldname, displayname, inputvalue = None, shortcut = None, state = None, inputvalueVisible = False, expectedType = "str"):
      self.fieldname = fieldname
      self.displayname = displayname
      self.inputvalue = inputvalue
      self.shortcut = shortcut
      self.state = state
      self.inputvalueVisible = inputvalueVisible
      self.expectedType = expectedType
      
      if self.expectedType not in allowedFieldTypes:
        print(f"{self.expectedType} is not in the list of allowed types.")
  
  def __iter__(self):
    yield 'fieldname', self.fieldname
    yield 'displayname', self.displayname
    yield 'inputvalue', self.inputvalue
    yield 'state', self.state
    
  def printEntryRow(self):
    output = ""
    if self.state == "hover":
      output += f"[green]=> {self.displayname}[/]"
    else:
      output += f" - {self.displayname}"
      
    if self.inputvalueVisible:
      output += f": {self.inputvalue}"
      
    output += "\n"
      
    return output
    
  def promptFieldInput(self):
    userInput = Prompt.ask(f"Enter input for\n{self.displayname}")
    self.inputvalue = userInput
    self.typecastInputToExpected()
    
  def checkFieldForExpectedType(self):
    if isinstance(self.inputvalue, self.expectedType):
      return True
    else:
      return False
    
  def typecastInputToExpected(self):
    match self.expectedType:
      case "str":
        self.inputvalue = str(self.inputvalue)
      case "int":
        self.inputvalue == int(self.inputvalue)
      case "float":
        self.inputvalue == float(self.inputvalue)
      case "bool":
        self.inputvalue == bool(self.inputvalue)
    
class MenuEntryWritableField(MenuEntry):
  def __init__(self, fieldname, displayname, inputvalue = None, shortcut = None, state = None, inputvalueVisible = False, expectedType = "str"):
    super().__init__(fieldname, displayname, inputvalue, shortcut, state, inputvalueVisible, expectedType)
    
class MenuEntryWriteObjectAttr(MenuEntry):
  def __init__(self, fieldname, displayname, inputvalue = None, shortcut = None, state = None, targetObject = None, inputvalueVisible = False, expectedType = "str"):
    super().__init__(fieldname, displayname, inputvalue, shortcut, state, inputvalueVisible, expectedType)
    self.targetObject = targetObject
    self.inputvalue = getattr(self.targetObject, self.fieldname)
    
  def assignFieldValueToObject(self):
    setattr(self.targetObject, self.fieldname, self.inputvalue)
    
    
@dataclass
class ExampleObject:
  name: str
  
exampleObjectInst = ExampleObject("Name of Object")

entryList = [MenuEntry(fieldname="One", displayname="Menu Field One", inputvalue = "input value 1", inputvalueVisible = True),
  MenuEntryWritableField(fieldname="Two", displayname="Menu Field Two", inputvalue = "input value 2", inputvalueVisible = True),
  MenuEntry(fieldname="Three", displayname="Another Menu Item", inputvalue = "input value 3", inputvalueVisible = True),
  MenuEntryWriteObjectAttr(fieldname="name", displayname="Example Object field", targetObject=exampleObjectInst, inputvalueVisible=True)]
  
TestMenu = MenuForm(title="Main Menu", entries = entryList)
  
TestMenu.showInterface()
