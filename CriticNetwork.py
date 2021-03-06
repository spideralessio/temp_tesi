from tensorflow.keras.layers import Dense, Flatten, Input, Lambda, Activation, concatenate, add
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import tensorflow.keras.backend as K
import tensorflow as tf

HIDDEN1_UNITS = 300
HIDDEN2_UNITS = 600

class CriticNetwork(object):
    def __init__(self, sess, state_size, action_size, BATCH_SIZE, TAU, LEARNING_RATE):
        self.sess = sess
        self.BATCH_SIZE = BATCH_SIZE
        self.TAU = TAU
        self.LEARNING_RATE = LEARNING_RATE
        self.action_size = action_size
        
        K.set_session(sess)

        self.model, self.action, self.state = self.create_critic_network(state_size, action_size)  
        self.target_model, self.target_action, self.target_state = self.create_critic_network(state_size, action_size)  
        self.action_grads = tf.gradients(self.model.output, self.action)  #GRADIENTS for policy update
        self.sess.run(tf.initialize_all_variables())

    def gradients(self, states, actions):
        return self.sess.run(self.action_grads, feed_dict={
            self.state: states,
            self.action: actions
        })[0]

    def target_train(self):
        critic_weights = self.model.get_weights()
        critic_target_weights = self.target_model.get_weights()
        for i in range(len(critic_weights)):
            critic_target_weights[i] = self.TAU * critic_weights[i] + (1 - self.TAU)* critic_target_weights[i]
        self.target_model.set_weights(critic_target_weights)

    def create_critic_network(self, state_size,action_dim):
        print("Now we build the model")
        with tf.name_scope('CriticNetwork') as scope:
            S = Input(shape=[state_size], name='State')  
            A = Input(shape=[action_dim], name='Action')   
            w1 = Dense(HIDDEN1_UNITS, activation='relu', name='DenseLayerS0')(S)
            a1 = Dense(HIDDEN2_UNITS, activation='linear', name='DenseLayerA')(A) 
            h1 = Dense(HIDDEN2_UNITS, activation='linear', name='DenseLayerS1')(w1)
            h2 = add([h1,a1], name='DenseLayerAS0')    
            h3 = Dense(HIDDEN2_UNITS, activation='relu', name='DenseLayerAS1')(h2)
            V = Dense(action_dim,activation='linear', name='Value')(h3)   
            model = Model(inputs=[S,A],outputs=V)
            adam = Adam(lr=self.LEARNING_RATE)
            model.compile(loss='mse', optimizer=adam)
            return model, A, S 
