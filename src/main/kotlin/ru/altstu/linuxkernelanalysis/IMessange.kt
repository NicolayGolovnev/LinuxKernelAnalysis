package ru.altstu.linuxkernelanalysis

interface IMessange {
    fun getDistance(otherMessange :IMessange):Double
    fun copy():IMessange
    fun getNull():IMessange
    fun getAverage(otherMessange :IMessange):IMessange
}