function soma(x::Int, y::Int)::Int
    a::Int
    a = x + y
    println(a)
    return a
end
a::Int
b::Int
a = 3
b = soma(a, 4)
println(a)
println(b)