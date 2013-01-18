'''
Created on Aug 3, 2012

@author: jonathan
'''
import unittest
import mab.xml2automata

class TestTranslator(unittest.TestCase):

    abpinxml = '''
<protocol name="Alternating Bit Protocol" medium="STUTT_FIFO" capacity="4">
  <messages>
    <message>ack0</message>
    <message>ack1</message>
    <message>mesg0</message>
    <message>mesg1</message>
  </messages>

<role name="SENDER">
  <states>
    <state type="initial">Q0</state>
    <state>Q1</state>
    <state>Q2</state>
    <state>Q3</state>
    <state>Q4</state>
    <state>Q5</state>
    <state>Ended</state>
    <state>Invalid</state>
  </states>
  <rule id="Q0_mesg0_OUTBOUND">
    <pre>
      <current_state>Q0</current_state>
    </pre>
    <post>
      <send_message>mesg0</send_message>
      <next_state>Q1</next_state>
    </post>
  </rule>

  <rule id="Q1_mesg0_OUTBOUND">
    <pre>
      <current_state>Q1</current_state>
    </pre>
    <post>
      <send_message>mesg0</send_message>
      <next_state>Q1</next_state>
    </post>
  </rule>

  <rule id="Q4_mesg0_OUTBOUND">
    <pre>
      <current_state>Q4</current_state>
    </pre>
    <post>
      <send_message>mesg0</send_message>
      <next_state>Q1</next_state>
    </post>
  </rule>

  <rule id="Q2_mesg1_OUTBOUND">
    <pre>
      <current_state>Q2</current_state>
    </pre>
    <post>
      <send_message>mesg1</send_message>
      <next_state>Q3</next_state>
    </post>
  </rule>

  <rule id="Q3_mesg1_OUTBOUND">
    <pre>
      <current_state>Q3</current_state>
    </pre>
    <post>
      <send_message>mesg1</send_message>
      <next_state>Q3</next_state>
    </post>
  </rule>

  <rule id="Q5_mesg1_OUTBOUND">
    <pre>
      <current_state>Q5</current_state>
    </pre>
    <post>
      <send_message>mesg1</send_message>
      <next_state>Q3</next_state>
    </post>
  </rule>

  <rule id="Q1_ack0_INBOUND">
    <pre>
      <current_state>Q1</current_state>
      <received_message>ack0</received_message>
    </pre>
    <post>
      <next_state>Q2</next_state>
    </post>
  </rule>

  <rule id="Q2_ack0_INBOUND">
    <pre>
      <current_state>Q2</current_state>
      <received_message>ack0</received_message>
    </pre>
    <post>
      <send_message>mesg1</send_message>
      <next_state>Q3</next_state>
    </post>
  </rule>

  <rule id="Q3_ack0_INBOUND">
    <pre>
      <current_state>Q3</current_state>
      <received_message>ack0</received_message>
    </pre>
    <post>
      <next_state>Q5</next_state>
    </post>
  </rule>

</role>
</protocol>'''

#  <rule id="Q5_ack0_INBOUND">
#    <pre>
#      <current_state>Q5</current_state>
#      <received_message>ack0</received_message>
#    </pre>
#    <post>
#      <send_message>mesg1</send_message>
#      <next_state>Q3</next_state>
#    </post>
#  </rule>
#
#  <rule id="Q0_ack1_INBOUND">
#    <pre>
#      <current_state>Q0</current_state>
#      <received_message>ack1</received_message>
#    </pre>
#    <post>
#      <send_message>mesg0</send_message>
#      <next_state>Q1</next_state>
#    </post>
#  </rule>
#
#  <rule id="Q1_ack1_INBOUND">
#    <pre>
#      <current_state>Q1</current_state>
#      <received_message>ack1</received_message>
#    </pre>
#    <post>
#      <next_state>Q0</next_state>
#    </post>
#  </rule>
#
#  <rule id="Q3_ack1_INBOUND">
#    <pre>
#      <current_state>Q3</current_state>
#      <received_message>ack1</received_message>
#    </pre>
#    <post>
#      <next_state>Q4</next_state>
#    </post>
#  </rule>
#
#  <rule id="Q4_ack1_INBOUND">
#    <pre>
#      <current_state>Q4</current_state>
#      <received_message>ack1</received_message>
#    </pre>
#    <post>
#      <send_message>mesg0</send_message>
#      <next_state>Q1</next_state>
#    </post>
#  </rule>

    def test_read(self):
      
        data = '<protocol>some data<something/></protocol>'
        t = mab.xml2automata.Translator(data)
        self.assertTrue(t.parse(data), 'Failed to parse valid xml')
        self.assertEqual(t.dom.documentElement.tagName, 'protocol') 
        self.assertTrue(t.dom.documentElement.firstChild.nodeValue == 'some data',
                        'text in node not correct')
    
    def test_translate1(self):
        t = mab.xml2automata.Translator(self.abpinxml)
        self.assertTrue(t.automata.has_key('SENDER'), 'Automaton SENDER not present')
        self.assertSetEqual(set(t.automata['SENDER'].get_states()),
                            set(['SENDER_Q0','SENDER_Q1','SENDER_Q2','SENDER_Q3','SENDER_Q4',
                                 'SENDER_Q5','SENDER_Ended','SENDER_Invalid',
                                 'SENDER_INTERMEDIATE_STATE_Q2_ack0_INBOUND']),
                            'Wrong state set!')
        self.assertTrue(t.automata['SENDER'].get_initial_states() == ['SENDER_Q0'],
                        'Wrong initial state set: ' + str(t.automata['SENDER'].get_initial_states()))
        self.assertIn(('SENDER_Q0', 'SENDER_Q1', {'action': 'send', 'symbol': 'mesg0'}), t.automata['SENDER'].get_transitions(),
                        'Did not find transition!')
        self.assertIn(('SENDER_Q2', 'SENDER_Q3', {'action': 'send', 'symbol': 'mesg1'}), t.automata['SENDER'].get_transitions(),
                        'Did not find transition!')

if __name__ == '__main__':
    unittest.main()