import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;
import java.text.DateFormat;
import java.util.Date;
import java.util.Locale;

public class SimpleSender {
	public static void main(String[] args) throws Exception {
		Date dDate = new Date();
		DateFormat dFormat = DateFormat.getDateTimeInstance(DateFormat.FULL,DateFormat.FULL, Locale.US);
		String command = null;

		String smtpServerAddr = "mails.tsinghua.edu.cn";
		int smtpServerPort = 25;

		String emailFromName = "Fake Aiden Li";
		String emailFromAddr = "i@fake-aidenli.net";
		String emailToName   = "Yuyang Li";
		String emailToAddr   = "liyuyang20@mails.tsinghua.edu.cn";

		String emailSubject = "The N-th Electronic Mail From Aiden to THU";
		String emailData = "Across the Great Firewall we can reach every corner in the world.";

		// DONE: 1
		Socket socket = new Socket(smtpServerAddr, smtpServerPort);

		InputStream is = socket.getInputStream();
		InputStreamReader isr = new InputStreamReader(is);
		BufferedReader br = new BufferedReader(isr);

		String response = br.readLine();
		System.out.println(response);
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
		// DONE: 4
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		// DONE: 5
		command = "MAIL FROM:<" + emailFromAddr + ">\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 6
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		command = "RCPT TO:<" + emailToAddr + ">\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 8
		 code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		// DONE: 9
		command = "DATA\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 10
		code = 354;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		String date = "DATE: " + dFormat.format(dDate) + "\r\n";
		System.out.print(date);
		os.write(date.getBytes("US-ASCII"));
		String str = "";
		// DONE: 11
		str = "From: " + emailFromName + "<" + emailFromAddr + ">\r\n";
		System.out.print(str);
		os.write(str.getBytes("US-ASCII"));
		// DONE: 12
		str = "To: " + emailToName + "<" + emailToAddr + ">\r\n";
		System.out.print(str);
		os.write(str.getBytes("US-ASCII"));

		// DONE: 13
		str = "SUBJECT:" + emailSubject + "\r\n\r\n";
		System.out.print(str);
		os.write(str.getBytes("US-ASCII"));
		// DONE: 14
		str = emailData + "\r\n";
		System.out.print(str);
		os.write(str.getBytes("UTF-8"));

		str = ".\r\n";
		System.out.print(str);
		os.write(str.getBytes("UTF-8"));
		response = br.readLine();
		System.out.println(response);
		// DONE: 15
		code = 250;
		if (!response.startsWith(Integer.toString(code))) {
			socket.close();
			throw new Exception(code + " reply not received from server.");
		}

		//DONE:	1
		command = "QUIT\r\n";
		System.out.print(command);
		os.write(command.getBytes("US-ASCII"));
		response = br.readLine();
		System.out.println(response);

		socket.close();
	}
}
