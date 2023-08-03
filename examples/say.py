from armarx_robots import A6


if __name__ == '__main__':

    robot = A6()
    text = "Hello."

    print(f"Saying ...\n'{text}'")
    robot.say(text)

