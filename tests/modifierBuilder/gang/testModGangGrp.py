#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from eos.const import State, Location, EffectBuildStatus, Context, FilterType, Operator
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.modifierBuilder.environment import DataHandler


class TestModGangGrp(EosTestCase):
    """Test parsing of trees describing gang-mates' ship modules modification filtered by group"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.dh = dh = DataHandler()
        # Manually composed example, as CCP doesn't use this modification type in any effect
        eTgtGrp = Expression(dataHandler=dh, expressionId=1, operandId=26, expressionGroupId=80)
        eTgtAttr = Expression(dataHandler=dh, expressionId=2, operandId=22, expressionAttributeId=158)
        eOptr = Expression(dataHandler=dh, expressionId=3, operandId=21, value="PostPercent")
        eSrcAttr = Expression(dataHandler=dh, expressionId=4, operandId=22, expressionAttributeId=349)
        eTgtSpec = Expression(dataHandler=dh, expressionId=5, operandId=34, arg1Id=eTgtGrp.id, arg2Id=eTgtAttr.id)
        eOptrTgt = Expression(dataHandler=dh, expressionId=6, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        self.eAddMod = Expression(dataHandler=dh, expressionId=7, operandId=2, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        self.eRmMod = Expression(dataHandler=dh, expressionId=8, operandId=54, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        dh.addExpressions((eTgtGrp, eTgtAttr, eOptr, eSrcAttr, eTgtSpec, eOptrTgt, self.eAddMod, self.eRmMod))

    def testGenericBuildSuccess(self):
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(modifier.sourceAttributeId, 349)
        self.assertEqual(modifier.operator, Operator.postPercent)
        self.assertEqual(modifier.targetAttributeId, 158)
        self.assertEqual(modifier.location, Location.ship)
        self.assertEqual(modifier.filterType, FilterType.group)
        self.assertEqual(modifier.filterValue, 80)

    def testEffCategoryPassive(self):
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryActive(self):
        effect = Effect(dataHandler=self.dh, categoryId=1, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryTarget(self):
        effect = Effect(dataHandler=self.dh, categoryId=2, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategoryArea(self):
        effect = Effect(dataHandler=self.dh, categoryId=3, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategoryOnline(self):
        effect = Effect(dataHandler=self.dh, categoryId=4, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryOverload(self):
        effect = Effect(dataHandler=self.dh, categoryId=5, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryDungeon(self):
        effect = Effect(dataHandler=self.dh, categoryId=6, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategorySystem(self):
        effect = Effect(dataHandler=self.dh, categoryId=7, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.gang)
