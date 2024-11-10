# ----------------------------------------------------------------------------
# Message management. Defines all the messages that we can send/receive.
#

# ----------------------------------------------------------------------------
# Message Identifications
#
# Every ID is a ASCII character that takes exactly one byte.
# The first messages are all numeric. After '9' the sequence starts with 'A'
# and continues to, and includes, 'Z'. If more messages are needed, then the
# sequence will start with the lower case alpha characters starting with 'a'
# and continuing to, and including, 'z'. If more are needed after than,
# a decision will be made at that time what the next characters may be.
#
# Because these are ASCII, this means a maximum 127 message IDs.
#
# Printable ASCII [32..126]:
#   ! " # $ % & ' ( ) * + , - . /
# 0 1 2 3 4 5 6 7 8 9 : ; < = > ?
# @ A B C D E F G H I J K L M N O
# P Q R S T U V W X Y Z [ \ ] ^ _
# ` a b c d e f g h i j k l m n o
# p q r s t u v w x y z { | } ~
#
# Third party message type is for adding something not provided by the FiPy
# In other words, a LoRa third-party device.
#
THIRD_PARTY = '0'

HEARTBEAT = '1'
HEARTBEAT_LOC = '2'
ALARM = '3'
CONFIRM_ALARM = '4'
CLEAR_ALARM = '5'
RESET_ALL = '6'
OUT_OF_COMM = '7'
IN_COMM = '8'

HEARTBEAT_MESH = 'A'
HEARTBEAT_LOC_MESH = 'B'
ALARM_MESH = 'C'
CONFIRM_ALARM_MESH = 'D'
CLEAR_ALARM_MESH = 'E'
RESET_ALL_MESH = 'F'
OOC_MESH = 'G'
IN_COMM_MESH = 'H'
