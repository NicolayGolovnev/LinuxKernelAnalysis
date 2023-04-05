package ru.altstu.linuxkernelanalysis

interface MessageMatcher {
    fun closestMessage(newMessage: String): String

    fun addNewMessage(newMessage: String)

    fun buildMessageDistances(): MutableList<MutableList<String>>
}