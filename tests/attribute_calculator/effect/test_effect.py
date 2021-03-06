# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from eos.const.eos import State, Domain, Scope, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem


class TestEffectToggling(AttrCalcTestCase):
    """Test effect toggling"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1, stackable=1)
        src_attr1 = self.ch.attribute(attribute_id=2)
        src_attr2 = self.ch.attribute(attribute_id=3)
        modifier1 = Modifier()
        modifier1.state = State.offline
        modifier1.scope = Scope.local
        modifier1.src_attr = src_attr1.id
        modifier1.operator = Operator.post_mul
        modifier1.tgt_attr = self.tgt_attr.id
        modifier1.domain = Domain.self_
        modifier1.filter_type = None
        modifier1.filter_value = None
        modifier2 = Modifier()
        modifier2.state = State.offline
        modifier2.scope = Scope.local
        modifier2.src_attr = src_attr2.id
        modifier2.operator = Operator.post_mul
        modifier2.tgt_attr = self.tgt_attr.id
        modifier2.domain = Domain.self_
        modifier2.filter_type = None
        modifier2.filter_value = None
        self.effect1 = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect1.modifiers = (modifier1,)
        self.effect2 = self.ch.effect(effect_id=2, category=EffectCategory.passive)
        self.effect2.modifiers = (modifier2,)
        self.holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect1, self.effect2),
            attributes={self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3}
        ))

    def test_effect_disabling(self):
        # Setup
        self.holder.state = State.offline
        self.fit.items.add(self.holder)
        # Action
        self.fit._link_tracker.disable_effects(self.holder, (self.effect1.id,))
        self.holder._disabled_effects.add(self.effect1.id)
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 130)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_effect_disabling_multiple(self):
        # Setup
        self.holder.state = State.offline
        self.fit.items.add(self.holder)
        # Action
        self.fit._link_tracker.disable_effects(self.holder, (self.effect1.id, self.effect2.id))
        self.holder._disabled_effects.update((self.effect1.id, self.effect2.id))
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_effect_enabling(self):
        # Setup
        self.holder.state = State.offline
        self.holder._disabled_effects.add(self.effect1.id)
        self.fit.items.add(self.holder)
        # Action
        self.holder._disabled_effects.discard(self.effect1.id)
        self.fit._link_tracker.enable_effects(self.holder, (self.effect1.id,))
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_effect_enabling_multiple(self):
        # Setup
        self.holder.state = State.offline
        self.holder._disabled_effects.update((self.effect1.id, self.effect2.id))
        self.fit.items.add(self.holder)
        # Action
        self.holder._disabled_effects.difference_update((self.effect1.id, self.effect2.id))
        self.fit._link_tracker.enable_effects(self.holder, (self.effect1.id, self.effect2.id))
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
