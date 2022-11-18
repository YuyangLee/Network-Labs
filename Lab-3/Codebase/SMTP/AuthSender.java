import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;
import java.text.DateFormat;
import java.util.Base64;
import java.util.Date;
import java.util.Locale;

public class AuthSender {
	public static void main(String[] args) throws Exception {
		Date dDate = new Date();
		DateFormat dFormat = DateFormat.getDateTimeInstance(DateFormat.FULL,DateFormat.FULL,
				Locale.US);
		String command = null;

		String smtpServerAddr = "mails.tsinghua.edu.cn";
		int smtpServerPort = 25;

		String emailFromName   = "Yuyang Li";
		String emailFromAddr   = "liyuyang20@mails.tsinghua.edu.cn";
		String emailToName = "Aiden Li";
		String emailToAddr = "i@aidenli.net";

		String emailSubject = "The N-th Electronic Mail From THU to Aiden";
		String emailData = "Across the Great Firewall we can reach every corner in the world.";

		String senderUsername = "liyuyang20@mails.tsinghua.edu.cn";
		String senderPassword = "********";

		// DONE: 1
		Socket socket = new Socket(smtpServerAddr, smtpServerPort);

		InputStream is = socket.getInputStream();
		InputStreamReader isr = new InputStreamReader(is);
		BufferedReader br = new BufferedReader(isr);

		String response = br.readLine();
		System.out.println(response);
		// DONE: 2
		int code = 220;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		OutputStream os = socket.getOutputStream();

		// DONE: 3
		command = "HELO " + smtpServerAddr + "\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		// DONE: 5
		command = "AUTH LOGIN\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 6
		code = 334;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}
		//DONE: 7
		Base64.Encoder encoder = Base64.getEncoder();
		String username_encoded = encoder.encodeToString(senderUsername.getBytes()) + "\r\n";
		os.write(username_encoded.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 7
		code = 334;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		} 
		String password_encoded = encoder.encodeToString(senderPassword.getBytes()) + "\r\n";
		os.write(password_encoded.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 8
		code = 235;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		} 
		

		// DONE: 9
		command = "MAIL FROM:<" + emailFromAddr + ">\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 10
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		// DONE: 11
		command = "RCPT TO:<" + emailToAddr + ">\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 12
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		// DONE: 13
		command = "DATA\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 14
		code = 354;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		String date = "DATE: " + dFormat.format(dDate) + "\r\n";
		System.out.print(date);
		os.write(date.getBytes("US-ASCII"));
		String str = "";
		
		// DONE: 15
		str = "From: " + emailFromName + "<" + emailFromAddr + ">\r\n";
		System.out.print(str);
		os.write(str.getBytes("US-ASCII"));
		// DONE: 16
		str = "To: " + emailToName + "<" + emailToAddr + ">\r\n";
		System.out.print(str);
		os.write(str.getBytes("US-ASCII"));

		// DONE: 17
		str = "SUBJECT:" + emailSubject + "\r\n\r\n";
		System.out.print(str);
		os.write(str.getBytes("UTF-8"));
		// DONE: 18
		str = emailData + "\r\n";
		System.out.print(str);
		os.write(str.getBytes("UTF-8"));

		str = ".\r\n";
		System.out.print(str);
		os.write(str.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 19
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		//DONE:	20
		command = "QUIT\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		socket.close();
	}
}
