package ru.altstu.linuxkernelanalysis

interface MessageMatcher {
    fun closestMessage(newMessage: String): String

    fun addNewMessage(newMessage: String)

    fun getResult(countClaster: Int): List<IMessange>
}