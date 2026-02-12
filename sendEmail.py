def sendEmail(to,subject,body):
    
    from_address = "someemail@something.com"
    to_address = to
    message = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(from_address, to_address, subject, body)

    try:
        server = smtplib.SMTP("someemailserver.com")
        server.sendmail(from_address, to_address, message)
        server.quit()
        print("Email sent successfully!")
    except:
        print("Failed to send email.")
