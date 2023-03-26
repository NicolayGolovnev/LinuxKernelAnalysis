package ru.altstu.linuxkernelanalysis.kotlin

interface MessageMatcher {
    fun closestMessage(newMessage: String): String

    fun addNewMessage(newMessage: String)

    fun buildMessageDistances(): MutableList<MutableList<String>>
}